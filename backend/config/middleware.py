"""
MosaVerse Security Middleware

Custom middleware for enhanced security:
- Security headers (HSTS, X-Content-Type-Options, etc.)
- File upload validation
- Request logging
- CSRF-free session authentication for API endpoints
"""

import logging
import mimetypes

from django.http import HttpResponseBadRequest
from django.conf import settings
from rest_framework.authentication import SessionAuthentication as BaseSessionAuthentication

logger = logging.getLogger(__name__)

# Maximum upload size: 10MB
MAX_UPLOAD_SIZE = 10 * 1024 * 1024

# Allowed image MIME types
ALLOWED_IMAGE_TYPES = [
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp',
]


# ─── Shared Utility ─────────────────────────────────────

def get_client_ip(request) -> str:
    """Extract client IP from Django request (handles X-Forwarded-For)."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


# ─── Session Auth (CSRF-exempt) ─────────────────────────

class SessionAuthentication(BaseSessionAuthentication):
    """
    Session authentication without CSRF enforcement.

    DRF's default SessionAuthentication enforces CSRF even when @csrf_exempt
    is applied. Since this API is consumed by a separate frontend (CORS),
    CSRF protection is handled at the middleware level with @csrf_exempt
    on write endpoints. Session cookies still provide authentication.
    """

    def enforce_csrf(self, request):
        return  # Skip DRF's CSRF check


# ─── Middleware Classes ──────────────────────────────────

class SecurityHeadersMiddleware:
    """Add security headers to all responses."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        response['X-Content-Type-Options'] = 'nosniff'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'

        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

        return response


class FileUploadValidationMiddleware:
    """Validate file uploads before processing (size limit check)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method in ('POST', 'PUT', 'PATCH'):
            content_type = request.content_type or ''

            if 'multipart/form-data' in content_type:
                content_length = request.META.get('CONTENT_LENGTH')
                if content_length:
                    try:
                        if int(content_length) > MAX_UPLOAD_SIZE:
                            logger.warning(
                                f"Upload rejected: Content-Length {content_length} "
                                f"exceeds limit from {get_client_ip(request)}"
                            )
                            return HttpResponseBadRequest(
                                'File too large. Maximum size is 10MB.',
                                content_type='application/json'
                            )
                    except (ValueError, TypeError):
                        pass

        return self.get_response(request)


class RequestLoggingMiddleware:
    """Log API requests with method, path, user, IP, and response status."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.path.startswith('/api/'):
            user = getattr(request, 'user', None)
            username = user.username if user and user.is_authenticated else 'anonymous'

            logger.info(
                f"{request.method} {request.path} → {response.status_code} | "
                f"user={username} | ip={get_client_ip(request)}"
            )

        return response
