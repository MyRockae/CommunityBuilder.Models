"""Resolve buyer tax country from UserAddress (address_type=tax)."""

from __future__ import annotations

from typing import Optional

from app_models.user_profile.models import UserAddress


def _normalize_country_code(code: str | None) -> str | None:
    if not code:
        return None
    normalized = str(code).strip().upper()
    if len(normalized) != 2:
        return None
    if normalized == 'UK':
        return 'GB'
    return normalized


def get_tax_address(user) -> Optional[UserAddress]:
    if user is None or not getattr(user, 'is_authenticated', True):
        return None
    if getattr(user, 'pk', None) is None:
        return None
    return (
        UserAddress.objects.filter(user=user, address_type='tax')
        .order_by('-updated_at')
        .first()
    )


def resolve_buyer_tax_country(user) -> Optional[str]:
    """
    ISO-2 from the user's tax address ``country_code``, or None if missing.
    Callers that need a catalog default should treat None as US/USD.
    """
    addr = get_tax_address(user)
    if addr is None:
        return None
    return _normalize_country_code(getattr(addr, 'country_code', None))
