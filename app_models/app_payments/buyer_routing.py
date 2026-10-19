"""
Resolve buyer country for catalog/checkout/gateway routing.

Source: ``UserWallet.country`` (personal wallet). Country alone drives
buyer display/charge currency selection and gateway routing (NG→Paystack,
else Stripe). CommunityWallet.country is seller payout only.
"""

from __future__ import annotations

from typing import Optional


def normalize_country_code(code: str | None) -> str | None:
    if not code:
        return None
    normalized = str(code).strip().upper()
    if len(normalized) != 2:
        return None
    if normalized == 'UK':
        return 'GB'
    return normalized


def get_or_create_user_wallet(user):
    """Return the user's primary wallet row (creates a bare row if none)."""
    if user is None or getattr(user, 'pk', None) is None:
        return None
    from app_models.app_payments.models import UserWallet

    wallet = (
        UserWallet.objects.filter(user=user)
        .order_by('-is_primary', '-updated_at')
        .first()
    )
    if wallet is not None:
        return wallet
    return UserWallet.objects.create(user=user, is_primary=True)


def resolve_buyer_country(user) -> Optional[str]:
    """
    ISO-2 from ``UserWallet.country``, or None if missing.
    Callers that need a catalog default should treat None as US/USD.
    """
    if user is None or not getattr(user, 'is_authenticated', True):
        return None
    if getattr(user, 'pk', None) is None:
        return None
    from app_models.app_payments.models import UserWallet

    wallet = (
        UserWallet.objects.filter(user=user)
        .order_by('-is_primary', '-updated_at')
        .first()
    )
    if wallet is None:
        return None
    return normalize_country_code(getattr(wallet, 'country', None))
