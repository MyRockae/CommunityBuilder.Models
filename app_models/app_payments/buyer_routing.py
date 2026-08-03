"""
Resolve buyer country for catalog/checkout/gateway routing.

Source address type is configurable via ``BUYER_ROUTING_ADDRESS_TYPE``
(currently ``tax``). Change that constant if routing should use ``billing``
(or another type) later — callers keep using ``resolve_buyer_country``.
"""

from __future__ import annotations

from typing import Optional

from app_models.user_profile.models import UserAddress

# Address type used for price/currency/gateway routing. Swap to 'billing' later if needed.
BUYER_ROUTING_ADDRESS_TYPE = 'tax'


def normalize_country_code(code: str | None) -> str | None:
    if not code:
        return None
    normalized = str(code).strip().upper()
    if len(normalized) != 2:
        return None
    if normalized == 'UK':
        return 'GB'
    return normalized


def get_buyer_routing_address(user) -> Optional[UserAddress]:
    """UserAddress used for checkout/catalog routing, or None."""
    if user is None or not getattr(user, 'is_authenticated', True):
        return None
    if getattr(user, 'pk', None) is None:
        return None
    return (
        UserAddress.objects.filter(user=user, address_type=BUYER_ROUTING_ADDRESS_TYPE)
        .order_by('-updated_at')
        .first()
    )


def resolve_buyer_country(user) -> Optional[str]:
    """
    ISO-2 from the buyer routing address ``country_code``, or None if missing.
    Callers that need a catalog default should treat None as US/USD.
    """
    addr = get_buyer_routing_address(user)
    if addr is None:
        return None
    return normalize_country_code(getattr(addr, 'country_code', None))
