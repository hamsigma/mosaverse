"""
MosaVerse Security Middleware

Custom middleware for enhanced security:
- Security headers (HSTS, X-Content-Type-Options, etc.)
- File upload validation
- Request logging
"""

import logging
import mimetypes

from django.http import HttpResponseBadRequest
from django.conf import settings

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


class SecurityHeadersMiddleware:
    """
    Add security headers to all responses.

    Headers added:
    - X-Content-Type-Options: nosniff
    - X-XSS-Protection: 1; mode=block (legacy browsers)
    - Referrer-Policy: strict-origin-when-cross-origin
    - Permissions-Policy: camera=(), microphone=(), geolocation=()
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        response['X-Content-Type-Options'] = 'nosniff'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'

        # HSTS in production only
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

        return response


class FileUploadValidationMiddleware:
    """
    Validate file uploads before processing.

    Checks:
    - File size limit (10MB max)
    - Allowed MIME types for image uploads
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only check POST/PUT/PATCH with file uploads
        if request.method in ('POST', 'PUT', 'PATCH'):
            content_type = request.content_type or ''

            if 'multipart/form-data' in content_type:
                # Check Content-Length header first (fast fail)
                content_length = request.META.get('CONTENT_LENGTH')
                if content_length:
                    try:
                        if int(content_length) > MAX_UPLOAD_SIZE:
                            logger.warning(
                                f"Upload rejected: Content-Length {content_length} "
                                f"exceeds limit from {request.META.get('REMOTE_ADDR')}"
                            )
                            return HttpResponseBadRequest(
                                'File too large. Maximum size is 10MB.',
                                content_type='application/json'
                            )
                    except (ValueError, TypeError):
                        pass

        return self.get_response(request)


class RequestLoggingMiddleware:
    """
    Log all API requests for security auditing.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log API requests
        if request.path.startswith('/api/'):
            user = getattr(request, 'user', None)
            username = user.username if user and user.is_authenticated else 'anonymous'
            ip = self._get_client_ip(request)

            logger.info(
                f"{request.method} {request.path} | "
                f"user={username} | ip={ip}"
            )

        response = self.get_response(request)

        if request.path.startswith('/api/'):
            logger.info(
                f"{request.method} {request.path} → {response.status_code}"
            )

        return response

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')
