"""
MosaVerse Input Validators

Validation functions for file uploads and user input.
"""

import os
import mimetypes
from django.core.exceptions import ValidationError

# Max image size: 50MB (must match middleware MAX_UPLOAD_SIZE)
MAX_IMAGE_SIZE = 50 * 1024 * 1024

# Allowed image extensions
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']

# Allowed image MIME types
ALLOWED_MIME_TYPES = [
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp',
]


def validate_image_file(image):
    """
    Validate uploaded image file.

    Checks:
    - File extension is allowed
    - File size within limit
    - MIME type is valid image type
    - File is not empty

    Args:
        image: Django UploadedFile object

    Raises:
        ValidationError if validation fails
    """
    if not image:
        raise ValidationError('No file provided.')

    # Check file extension
    ext = os.path.splitext(image.name)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            f'File type "{ext}" is not allowed. '
            f'Allowed types: {", ".join(ALLOWED_IMAGE_EXTENSIONS)}'
        )

    # Check file size
    if image.size > MAX_IMAGE_SIZE:
        max_mb = MAX_IMAGE_SIZE // (1024 * 1024)
        raise ValidationError(
            f'File size ({image.size / (1024*1024):.1f}MB) exceeds '
            f'maximum limit of {max_mb}MB.'
        )

    # Check MIME type
    if hasattr(image, 'content_type'):
        if image.content_type not in ALLOWED_MIME_TYPES:
            raise ValidationError(
                f'Invalid file type "{image.content_type}". '
                f'Allowed types: image/jpeg, image/png, image/gif, image/webp'
            )

    # Check file is not empty
    if image.size == 0:
        raise ValidationError('File is empty.')


def sanitize_string(value, max_length=500):
    """
    Sanitize user input string.

    - Strip whitespace
    - Limit length
    - Remove null bytes

    Args:
        value: Input string
        max_length: Maximum allowed length

    Returns:
        Sanitized string
    """
    if not value:
        return ''

    # Remove null bytes
    value = value.replace('\x00', '')

    # Strip and truncate
    value = value.strip()[:max_length]

    return value


def validate_title(value):
    """Validate design title."""
    value = sanitize_string(value, max_length=200)
    if not value:
        raise ValidationError('Title cannot be empty.')
    if len(value) < 3:
        raise ValidationError('Title must be at least 3 characters.')
    return value


def validate_description(value):
    """Validate design description."""
    return sanitize_string(value, max_length=2000)


def validate_category_name(value):
    """Validate category name."""
    value = sanitize_string(value, max_length=100)
    if not value:
        raise ValidationError('Category name cannot be empty.')
    if len(value) < 2:
        raise ValidationError('Category name must be at least 2 characters.')
    return value
