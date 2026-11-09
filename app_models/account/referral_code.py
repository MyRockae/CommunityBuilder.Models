"""Stable public referral codes. Never derived from username, email, or numeric id."""

from django.utils.crypto import get_random_string

REFERRAL_CODE_LENGTH = 10
# Crockford Base32 without i, l, o (ambiguous with 1/0).
REFERRAL_CODE_ALPHABET = '0123456789abcdefghjkmnpqrstuvwxyz'
ALLOCATE_ATTEMPTS = 32


def generate_referral_code() -> str:
    return get_random_string(REFERRAL_CODE_LENGTH, allowed_chars=REFERRAL_CODE_ALPHABET)


def normalize_referral_code(value: str | None) -> str:
    if not value:
        return ''
    return str(value).strip().lower()


def allocate_referral_code(user_model) -> str:
    for _ in range(ALLOCATE_ATTEMPTS):
        code = generate_referral_code()
        if not user_model.objects.filter(referral_code=code).exists():
            return code
    raise RuntimeError('Could not allocate a unique referral_code')
