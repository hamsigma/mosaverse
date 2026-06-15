"""
MosaVerse AI Service Layer — Google Gemini API Integration

Provides centralized AI services with:
- Retry logic with exponential backoff
- Rate limiting (in-memory per-IP)
- Proper error handling and logging
- Clean service interfaces for views
"""

import time
import logging
import hashlib
from typing import List, Optional, Tuple
from dataclasses import dataclass, field

from django.conf import settings
from openai import OpenAI, APIError, APITimeoutError, APIConnectionError, RateLimitError

from apps.designs.models import Design, Category
from config.middleware import get_client_ip

logger = logging.getLogger(__name__)

# ─── Configuration ───────────────────────────────────────────────────────────

MAX_RETRIES = 3
RETRY_DELAY_BASE = 1.0  # seconds
REQUEST_TIMEOUT = 30.0  # seconds
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_REQUESTS = 10  # max requests per window per IP


# ─── Rate Limiter ────────────────────────────────────────────────────────────

@dataclass
class RateLimitEntry:
    """Track requests for a single client."""
    requests: list = field(default_factory=list)

    def clean_old(self, window: int):
        cutoff = time.time() - window
        self.requests = [t for t in self.requests if t > cutoff]

    @property
    def count(self):
        return len(self.requests)

    def add(self):
        self.requests.append(time.time())


class RateLimiter:
    """Simple in-memory rate limiter (per-IP)."""

    def __init__(self, window: int = RATE_LIMIT_WINDOW, max_requests: int = RATE_LIMIT_MAX_REQUESTS):
        self.window = window
        self.max_requests = max_requests
        self._entries: dict[str, RateLimitEntry] = {}

    def _get_key(self, identifier: str) -> str:
        return hashlib.md5(identifier.encode()).hexdigest()

    def is_allowed(self, identifier: str) -> bool:
        key = self._get_key(identifier)

        if key not in self._entries:
            self._entries[key] = RateLimitEntry()

        entry = self._entries[key]
        entry.clean_old(self.window)

        if entry.count >= self.max_requests:
            return False

        entry.add()
        return True

    def remaining(self, identifier: str) -> int:
        key = self._get_key(identifier)
        entry = self._entries.get(key)
        if not entry:
            return self.max_requests
        entry.clean_old(self.window)
        return max(0, self.max_requests - entry.count)


# Global rate limiter instance
rate_limiter = RateLimiter()


# ─── AI Client ───────────────────────────────────────────────────────────────

def get_ai_client() -> OpenAI:
    """Create a Google Gemini API client (OpenAI-compatible)."""
    return OpenAI(
        api_key=settings.GEMINI_API_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        timeout=REQUEST_TIMEOUT,
    )


def _call_ai_with_retry(
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 300,
    temperature: float = 0.7,
) -> str:
    """
    Call Gemini API with retry logic and exponential backoff.

    Args:
        system_prompt: System message for the AI
        user_prompt: User message/query
        max_tokens: Maximum response tokens
        temperature: Creativity level (0.0 - 1.0)

    Returns:
        AI response text

    Raises:
        AIServiceError: If all retries fail
    """
    client = get_ai_client()
    last_error = None

    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"AI call attempt {attempt + 1}/{MAX_RETRIES}")

            response = client.chat.completions.create(
                model="gemini-2.5-flash",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )

            raw_content = response.choices[0].message.content
            if not raw_content:
                # Gemini 2.5 thinking mode may return None content; retry
                raise ValueError("AI returned empty response (thinking mode)")
            result = raw_content.strip()
            logger.info(f"AI call succeeded on attempt {attempt + 1}")
            return result

        except (APITimeoutError, APIConnectionError, RateLimitError) as e:
            last_error = e
            wait_time = RETRY_DELAY_BASE * (2 ** (attempt + 1))  # longer backoff for rate limits
            logger.warning(
                f"AI call attempt {attempt + 1} failed (retryable): {e}. "
                f"Retrying in {wait_time}s..."
            )
            time.sleep(wait_time)

        except APIError as e:
            last_error = e
            logger.error(f"AI call failed with API error (non-retryable): {e}")
            raise AIServiceError(f"API error: {e}") from e

        except Exception as e:
            last_error = e
            logger.error(f"AI call failed with unexpected error: {e}")
            if attempt == MAX_RETRIES - 1:
                raise AIServiceError(f"Unexpected error: {e}") from e
            wait_time = RETRY_DELAY_BASE * (2 ** attempt)
            time.sleep(wait_time)

    raise AIServiceError(
        f"All {MAX_RETRIES} retry attempts failed. Last error: {last_error}"
    )


# ─── Custom Exceptions ───────────────────────────────────────────────────────

class AIServiceError(Exception):
    """Raised when AI service encounters an error."""
    pass


class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded."""
    pass


# ─── Service Functions ────────────────────────────────────────────────────────

def smart_search(query: str, request=None) -> dict:
    """
    AI Smart Search — find designs using natural language.

    Converts a natural language query into relevant design matches
    by leveraging Gemini's understanding of context.

    Args:
        query: Natural language search query
        request: Django request object (for serializer context)

    Returns:
        dict with 'query', 'count', and 'results' (serialized designs)
    """
    from apps.designs.serializers import DesignListSerializer

    # Rate limiting
    client_ip = get_client_ip(request) if request else 'unknown'
    if not rate_limiter.is_allowed(client_ip):
        raise RateLimitExceeded(
            f"Rate limit exceeded. Try again in {RATE_LIMIT_WINDOW} seconds."
        )

    # Build design context for AI
    designs = Design.objects.filter(is_published=True).select_related('category')
    if not designs.exists():
        return {'query': query, 'count': 0, 'results': []}

    design_context = '\n'.join([
        f"- ID:{d.id} | {d.title} | "
        f"Kategori: {d.category.name if d.category else 'N/A'} | "
        f"{d.description[:100] if d.description else 'No description'}"
        for d in designs[:50]
    ])

    user_prompt = (
        f"Kamu adalah AI assistant untuk galeri desain baju MosaVerse.\n"
        f"User mencari desain dengan query: \"{query}\"\n\n"
        f"Berikut daftar desain yang tersedia:\n{design_context}\n\n"
        f"Pilih ID desain yang paling relevan dengan query user.\n"
        f"Kembalikan HANYA daftar ID (angka) yang dipisahkan koma, tanpa teks lain.\n"
        f"Contoh: 1,3,5,8"
    )

    result_text = _call_ai_with_retry(
        system_prompt="Kamu adalah asisten pencarian desain. Hanya kembalikan ID yang relevan, dipisahkan koma.",
        user_prompt=user_prompt,
        max_tokens=200,
        temperature=0.3,
    )

    # Parse IDs from AI response
    ids = _parse_id_list(result_text)

    if not ids:
        return {'query': query, 'count': 0, 'results': []}

    # Fetch matching designs preserving AI's relevance order
    matched = Design.objects.filter(
        id__in=ids, is_published=True
    ).select_related('category')

    # Preserve order from AI response
    id_order = {id_val: idx for idx, id_val in enumerate(ids)}
    matched_list = sorted(matched, key=lambda d: id_order.get(d.id, 999))

    serializer = DesignListSerializer(
        matched_list, many=True, context={'request': request}
    )

    return {
        'query': query,
        'count': len(serializer.data),
        'results': serializer.data,
    }


def generate_description(
    title: str,
    category: str = '',
    design_id: Optional[int] = None,
) -> dict:
    """
    Generate a compelling description for a design using AI.

    Args:
        title: Design title
        category: Design category name
        design_id: Optional design ID to auto-update

    Returns:
        dict with 'description' and 'design_id'
    """
    user_prompt = (
        f"Buatkan deskripsi singkat dan menarik (2-3 kalimat) untuk desain baju berikut:\n"
        f"- Judul: {title}\n"
        f"- Kategori: {category if category else 'belum ditentukan'}\n\n"
        f"Deskripsi harus informatif, menggambarkan gaya dan karakteristik desain, "
        f"dan menarik untuk calon pembeli.\n"
        f"Tulis dalam Bahasa Indonesia."
    )

    description = _call_ai_with_retry(
        system_prompt="Kamu adalah copywriter fashion profesional. Buat deskripsi yang menarik, singkat, dan profesional dalam Bahasa Indonesia.",
        user_prompt=user_prompt,
        max_tokens=300,
        temperature=0.7,
    )

    # Auto-update design if ID provided
    if design_id:
        try:
            design = Design.objects.get(id=design_id)
            design.description = description
            design.save()
            logger.info(f"Auto-updated description for design #{design_id}")
        except Design.DoesNotExist:
            logger.warning(f"Design #{design_id} not found for auto-update")

    return {
        'description': description,
        'design_id': design_id,
    }


def generate_category(
    title: str,
    description: str = '',
    design_id: Optional[int] = None,
) -> dict:
    """
    Generate/suggest the best category for a design using AI.

    Args:
        title: Design title
        description: Design description
        design_id: Optional design ID to auto-update

    Returns:
        dict with 'category', 'category_id', 'is_new', and 'design_id'
    """
    # Get existing categories
    categories = list(Category.objects.values_list('name', flat=True))
    categories_text = ', '.join(categories) if categories else 'belum ada kategori'

    user_prompt = (
        f"Tentukan kategori yang paling tepat untuk desain baju berikut:\n"
        f"- Judul: {title}\n"
        f"- Deskripsi: {description if description else 'belum ada deskripsi'}\n\n"
        f"Kategori yang sudah tersedia: {categories_text}\n\n"
        f"Pilih SATU kategori yang paling cocok, atau buat kategori baru jika tidak ada yang cocok.\n"
        f"Kembalikan HANYA nama kategori (tanpa penjelasan lain)."
    )

    category_name = _call_ai_with_retry(
        system_prompt="Kamu adalah ahli kategorisasi fashion. Tentukan kategori yang paling tepat. Kembalikan hanya nama kategori.",
        user_prompt=user_prompt,
        max_tokens=50,
        temperature=0.3,
    )

    # Clean up the response (remove quotes, extra spaces)
    category_name = category_name.strip().strip('"').strip("'").strip()

    # Get or create the category
    category, created = Category.objects.get_or_create(
        name__iexact=category_name,
        defaults={'name': category_name.title()}
    )

    # Auto-update design if ID provided
    if design_id:
        try:
            design = Design.objects.get(id=design_id)
            design.category = category
            design.save()
            logger.info(f"Auto-updated category for design #{design_id}")
        except Design.DoesNotExist:
            logger.warning(f"Design #{design_id} not found for auto-update")

    return {
        'category': category.name,
        'category_id': category.id,
        'is_new': created,
        'design_id': design_id,
    }


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _parse_id_list(text: str) -> List[int]:
    """Parse comma-separated IDs from AI response text."""
    ids = []
    for part in text.split(','):
        part = part.strip()
        if part.isdigit():
            ids.append(int(part))
    return ids
