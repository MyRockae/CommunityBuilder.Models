"""
Whether a community can accept paid checkout / create paid catalog items.

Fully active payout destination only — country alone is not enough.
"""

from __future__ import annotations

from app_models.app_payments.models import CommunityWallet, PaymentGateway, WalletStatus


def get_community_wallet(community) -> CommunityWallet | None:
    if community is None:
        return None
    try:
        return community.wallet
    except CommunityWallet.DoesNotExist:
        return None


def community_wallet_ready(community) -> bool:
    """
    True when the community has a fully active payout destination.

    - Stripe: status active and stripe_connect_account_id set
      (active is set only when Stripe reports charges_enabled + payouts_enabled).
    - Paystack: status active and paystack_recipient_code or paystack_subaccount_code set.
    """
    wallet = get_community_wallet(community)
    if wallet is None:
        return False
    if wallet.status != WalletStatus.ACTIVE:
        return False

    gateway = (wallet.payment_gateway or '').strip().lower()
    if gateway == PaymentGateway.STRIPE:
        return bool((wallet.stripe_connect_account_id or '').strip())
    if gateway == PaymentGateway.PAYSTACK:
        has_sub = bool((wallet.paystack_subaccount_code or '').strip())
        has_rcp = bool((wallet.paystack_recipient_code or '').strip())
        return has_sub or has_rcp
    return False
