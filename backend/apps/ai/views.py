"""
AI Views — Thin controllers that delegate to the AI service layer.

All AI logic (retry, rate limiting, DeepSeek calls) lives in services.py.
Views only handle HTTP request/response mapping and input validation.
"""

import functools

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.throttling import AnonRateThrottle
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt

from apps.ai.services import (
    smart_search,
    generate_description as generate_description_service,
    generate_category as generate_category_service,
    AIServiceError,
    RateLimitExceeded,
)


class AIRateThrottle(AnonRateThrottle):
    """Custom throttle for AI endpoints: 10 requests per minute."""
    rate = '10/min'


def ai_endpoint(view_func):
    """
    Decorator that wraps AI view functions with:
    - CSRF exemption
    - Rate throttling
    - Centralized error handling (AIServiceError, RateLimitExceeded)
    """
    @functools.wraps(view_func)
    @api_view(['POST'])
    @throttle_classes([AIRateThrottle])
    @csrf_exempt
    def wrapper(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except RateLimitExceeded as e:
            return Response({'error': str(e)}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        except AIServiceError as e:
            return Response(
                {'error': f'Layanan AI sedang tidak tersedia. Silakan coba lagi. ({e})'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except Exception as e:
            return Response(
                {'error': f'Terjadi kesalahan tidak terduga: {e}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    return wrapper


# ─── Endpoints ──────────────────────────────────────────

@ai_endpoint
@permission_classes([AllowAny])
def ai_search(request):
    """AI Smart Search — cari desain dengan natural language."""
    query = request.data.get('query', '').strip()

    if not query:
        return Response({'error': 'Query pencarian wajib diisi.'}, status=status.HTTP_400_BAD_REQUEST)
    if len(query) < 3:
        return Response({'error': 'Query terlalu pendek (minimal 3 karakter).'}, status=status.HTTP_400_BAD_REQUEST)

    result = smart_search(query, request=request)
    return Response(result)


@ai_endpoint
@permission_classes([IsAdminUser])
def generate_description(request):
    """Generate deskripsi desain menggunakan AI."""
    title = request.data.get('title', '').strip()
    category = request.data.get('category', '').strip()
    design_id = request.data.get('design_id')

    if not title:
        return Response({'error': 'Title wajib diisi.'}, status=status.HTTP_400_BAD_REQUEST)

    result = generate_description_service(title=title, category=category, design_id=design_id)
    return Response(result)


@ai_endpoint
@permission_classes([IsAdminUser])
def generate_category(request):
    """Generate kategori desain menggunakan AI."""
    title = request.data.get('title', '').strip()
    description = request.data.get('description', '').strip()
    design_id = request.data.get('design_id')

    if not title:
        return Response({'error': 'Title wajib diisi.'}, status=status.HTTP_400_BAD_REQUEST)

    result = generate_category_service(title=title, description=description, design_id=design_id)
    return Response(result)
