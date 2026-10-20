import django
from django.db import models
from django.db.models import Q

from app_models.account.models import User


def _payment_checkout_session_subject_check_constraint():
    """Django < 5.2 uses CheckConstraint(check=...); 5.2+ prefers condition= (required in Django 6+)."""
    q = (
        Q(
            app_subscription__isnull=False,
            community_member_subscription__isnull=True,
            store_purchase__isnull=True,
            event_registration__isnull=True,
        )
        | Q(
            app_subscription__isnull=True,
            community_member_subscription__isnull=False,
            store_purchase__isnull=True,
            event_registration__isnull=True,
        )
        | Q(
            app_subscription__isnull=True,
            community_member_subscription__isnull=True,
            store_purchase__isnull=False,
            event_registration__isnull=True,
        )
        | Q(
            app_subscription__isnull=True,
            community_member_subscription__isnull=True,
            store_purchase__isnull=True,
            event_registration__isnull=False,
        )
    )
    name = 'paymentcheckoutsession_exactly_one_subject'
    if django.VERSION >= (5, 2):
        return models.CheckConstraint(condition=q, name=name)
    return models.CheckConstraint(check=q, name=name)


class PaymentGateway(models.TextChoices):
    STRIPE = 'stripe', 'Stripe'
    PAYSTACK = 'paystack', 'Paystack'


class WalletStatus:
    PENDING = 'pending'
    ACTIVE = 'active'
    RESTRICTED = 'restricted'
    DISABLED = 'disabled'
    CHOICES = [
        (PENDING, 'Pending onboarding'),
        (ACTIVE, 'Active — payouts enabled'),
        (RESTRICTED, 'Restricted'),
        (DISABLED, 'Disabled'),
    ]


class UserWallet(models.Model):
    """
    Personal wallet for a user: country (checkout/gateway routing) and optional
    payout destination (referrals / personal earnings).
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wallets',
        help_text='User this wallet belongs to',
    )
    country = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        help_text='ISO 3166-1 alpha-2 country for checkout/gateway routing (null until set)',
    )
    legal_name = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text='Legal name (person or business) for payout onboarding',
    )
    payment_gateway = models.CharField(
        max_length=20,
        choices=PaymentGateway.choices,
        blank=True,
        null=True,
        help_text='Processor this payout destination is registered with (null until payout setup)',
    )
    label = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text='Optional label shown to the user (e.g. main bank, NGN wallet)',
    )
    status = models.CharField(
        max_length=20,
        choices=WalletStatus.CHOICES,
        default=WalletStatus.PENDING,
        help_text='Onboarding / capability state mirrored from the gateway where possible',
    )
    is_primary = models.BooleanField(
        default=False,
        help_text='Preferred payout account for this user on this gateway',
    )

    stripe_connect_account_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Stripe Connect account id (acct_…)',
    )
    paystack_subaccount_code = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Paystack subaccount code for split settlements',
    )
    paystack_recipient_code = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Paystack transfer recipient code for payouts to bank/mobile money',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'UserWallet'
        verbose_name = 'User wallet'
        verbose_name_plural = 'User wallets'
        ordering = ['-is_primary', '-updated_at']
        indexes = [
            models.Index(fields=['user', 'payment_gateway', 'status']),
            models.Index(fields=['user', 'is_primary']),
            models.Index(fields=['stripe_connect_account_id']),
            models.Index(fields=['paystack_subaccount_code']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'payment_gateway'],
                condition=models.Q(is_primary=True, payment_gateway__isnull=False),
                name='userwallet_unique_primary_per_user_gateway',
            ),
        ]

    def __str__(self):
        gw = self.payment_gateway or 'no-gateway'
        return f'{self.user.email} — {gw} ({self.status})'


class UserEarning(models.Model):
    """
    Personal credit owed to a user (e.g. referral), paid out via UserWallet.
    Mirrors PaymentTransaction community payout fields: amount, transferred_to_*,
    transfer refs, and wallet FK — not community-linked.
    """

    KIND_REFERRAL = 'referral'
    KIND_CHOICES = [
        (KIND_REFERRAL, 'Referral'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='earnings',
        help_text='User this credit is owed to',
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Amount owed to the user',
    )
    currency = models.CharField(
        max_length=3,
        default='USD',
        help_text='Currency code (USD, EUR, etc.)',
    )
    kind = models.CharField(
        max_length=32,
        choices=KIND_CHOICES,
        default=KIND_REFERRAL,
        help_text='How this credit was earned',
    )
    note = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text='Optional short note shown to the user',
    )
    transferred_to_user = models.BooleanField(
        default=False,
        help_text='Whether amount has been paid out to the user wallet',
    )
    transferred_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the transfer to the user was completed',
    )
    user_wallet = models.ForeignKey(
        UserWallet,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='earnings',
        help_text='User wallet used when transferring amount (audit trail)',
    )
    stripe_transfer_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text='Stripe Transfer id when amount is paid out via Stripe',
    )
    paystack_transfer_reference = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text='Paystack transfer reference when amount is paid out via Paystack',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'UserEarning'
        verbose_name = 'User earning'
        verbose_name_plural = 'User earnings'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'transferred_to_user']),
            models.Index(fields=['user', 'currency', '-created_at']),
        ]

    def __str__(self):
        return f'{self.user_id} {self.amount} {self.currency} ({self.kind})'


class CommunityWallet(models.Model):
    """
    Community payout destination. One wallet per community.
    Country is the seller payout rail destination only — not buyer checkout currency.
    """

    community = models.OneToOneField(
        'community.Community',
        on_delete=models.CASCADE,
        related_name='wallet',
        help_text='Community this payout wallet belongs to',
    )
    country = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        help_text='ISO 3166-1 alpha-2 country for seller payout destination',
    )
    legal_name = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text='Legal name (person or business) for community payout onboarding',
    )
    payment_gateway = models.CharField(
        max_length=20,
        choices=PaymentGateway.choices,
        blank=True,
        null=True,
        help_text='Processor this payout destination is registered with',
    )
    label = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text='Optional label for this payout destination',
    )
    status = models.CharField(
        max_length=20,
        choices=WalletStatus.CHOICES,
        default=WalletStatus.PENDING,
        help_text='Onboarding / capability state mirrored from the gateway where possible',
    )

    stripe_connect_account_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Stripe Connect account id (acct_…)',
    )
    paystack_subaccount_code = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Paystack subaccount code for split settlements',
    )
    paystack_recipient_code = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Paystack transfer recipient code for payouts to bank/mobile money',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'CommunityWallet'
        verbose_name = 'Community wallet'
        verbose_name_plural = 'Community wallets'
        indexes = [
            models.Index(fields=['payment_gateway', 'status']),
            models.Index(fields=['stripe_connect_account_id']),
            models.Index(fields=['paystack_subaccount_code']),
        ]

    def __str__(self):
        gw = self.payment_gateway or 'no-gateway'
        return f'{self.community.alias} — {gw} ({self.status})'


class PaymentCheckoutSession(models.Model):
    """
    Short-lived browser/mobile checkout handoff (opaque URL token → exchange for payment UI data).

    Same subject axes as PaymentTransaction: app subscription, community member (tier) subscription,
    or store purchase. Raw token is never stored — only token_hash (e.g. SHA-256 hex of secret token).
    """

    SESSION_KIND_CHOICES = [
        ('app_subscription', 'App Subscription'),
        ('community_member_subscription', 'Community Member Subscription'),
        ('store_purchase', 'Store Product Purchase'),
        ('event_registration', 'Event Registration'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_COMPLETED = 'completed'
    STATUS_EXPIRED = 'expired'
    STATUS_REVOKED = 'revoked'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_EXPIRED, 'Expired'),
        (STATUS_REVOKED, 'Revoked'),
        (STATUS_FAILED, 'Failed'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payment_checkout_sessions',
        null=True,
        blank=True,
        help_text='Buyer who may redeem this session; null for guest store checkout',
    )
    session_kind = models.CharField(
        max_length=50,
        choices=SESSION_KIND_CHOICES,
        help_text='Which subject FK is populated — same vocabulary as PaymentTransaction.transaction_type',
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        help_text='Lifecycle: pending until completed, expired, revoked, or failed',
    )

    token_hash = models.CharField(
        max_length=64,
        unique=True,
        help_text='Hex digest of opaque checkout token (raw token only sent once in URL)',
    )

    app_subscription = models.ForeignKey(
        'app_subscription.AppSubscription',
        on_delete=models.CASCADE,
        related_name='payment_checkout_sessions',
        null=True,
        blank=True,
        help_text='Set when session_kind is app_subscription',
    )
    community_member_subscription = models.ForeignKey(
        'app_subscription.CommunityMemberSubscription',
        on_delete=models.CASCADE,
        related_name='payment_checkout_sessions',
        null=True,
        blank=True,
        help_text='Set when session_kind is community_member_subscription',
    )
    store_purchase = models.ForeignKey(
        'community_store.StorePurchase',
        on_delete=models.CASCADE,
        related_name='payment_checkout_sessions',
        null=True,
        blank=True,
        help_text='Set when session_kind is store_purchase',
    )
    event_registration = models.ForeignKey(
        'community_event.EventRegistration',
        on_delete=models.CASCADE,
        related_name='payment_checkout_sessions',
        null=True,
        blank=True,
        help_text='Set when session_kind is event_registration',
    )

    payment_gateway = models.CharField(
        max_length=20,
        choices=PaymentGateway.choices,
        blank=True,
        null=True,
        help_text='Processor for this checkout (stripe / paystack)',
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text='Optional type-specific context (return URLs, display hints, etc.); do not store client_secret here',
    )

    expires_at = models.DateTimeField(help_text='When this session stops accepting exchange')
    used_at = models.DateTimeField(null=True, blank=True, help_text='When checkout handoff was consumed or payment completed')
    revoked_at = models.DateTimeField(null=True, blank=True, help_text='When user or system cancelled before completion')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'PaymentCheckoutSession'
        verbose_name = 'Payment checkout session'
        verbose_name_plural = 'Payment checkout sessions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status', 'expires_at']),
            models.Index(fields=['status', 'expires_at']),
            models.Index(fields=['session_kind', 'status']),
        ]
        constraints = [
            _payment_checkout_session_subject_check_constraint(),
        ]

    def __str__(self):
        return f'{self.session_kind} — {self.user_id} — {self.status} ({self.token_hash[:12]}…)'


class PaymentTransaction(models.Model):
    """Ledger row per charge (Stripe or Paystack): app subscription, community membership, or store sale.

    For community-linked payments, use platform_fee / community_amount and transferred_to_community /
    stripe_transfer_id or paystack_transfer_reference the same way: collect on the platform account,
    then pay the community on your schedule (e.g. weekly batch).
    """
    TRANSACTION_TYPE_CHOICES = [
        ('app_subscription', 'App Subscription'),
        ('community_member_subscription', 'Community Member Subscription'),
        ('store_purchase', 'Store Product Purchase'),
        ('event_registration', 'Event Registration'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPE_CHOICES, help_text='Type of transaction')
    app_subscription = models.ForeignKey(
        'app_subscription.AppSubscription',
        on_delete=models.CASCADE,
        related_name='transactions',
        null=True,
        blank=True,
        help_text='App subscription (if transaction_type is app_subscription)',
    )
    community_member_subscription = models.ForeignKey(
        'app_subscription.CommunityMemberSubscription',
        on_delete=models.CASCADE,
        related_name='transactions',
        null=True,
        blank=True,
        help_text='Community member subscription (if transaction_type is community_member_subscription)',
    )
    store_purchase = models.ForeignKey(
        'community_store.StorePurchase',
        on_delete=models.CASCADE,
        related_name='payment_transactions',
        null=True,
        blank=True,
        help_text='Store product purchase (if transaction_type is store_purchase)',
    )
    event_registration = models.ForeignKey(
        'community_event.EventRegistration',
        on_delete=models.SET_NULL,
        related_name='payment_transactions',
        null=True,
        blank=True,
        help_text='Event registration (if transaction_type is event_registration). Cleared when a finished event is deleted so the charge record stays.',
    )

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text='Total payment amount charged to the buyer')
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Platform cut (e.g. 2% for community subscriptions and store sales; 0 for app subscriptions)')
    community_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='Amount owed to the community after platform_fee (e.g. 98% for member subs and store sales)',
    )

    currency = models.CharField(max_length=3, default='USD', help_text='Currency code (USD, EUR, etc.)')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', help_text='Payment status')

    billing_country = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        help_text='ISO 3166-1 alpha-2 country for this charge',
    )
    payment_gateway = models.CharField(
        max_length=20,
        choices=PaymentGateway.choices,
        blank=True,
        null=True,
        help_text='Processor that captured this payment',
    )

    stripe_payment_intent_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        help_text='Stripe PaymentIntent id (null when payment_gateway is paystack)',
    )
    stripe_charge_id = models.CharField(max_length=255, null=True, blank=True, help_text='Stripe charge ID')

    paystack_transaction_reference = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        help_text='Paystack transaction reference (null when payment_gateway is stripe)',
    )

    transferred_to_community = models.BooleanField(
        default=False,
        help_text='Whether community_amount has been paid out to the community wallet',
    )
    transferred_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the transfer to the community was completed',
    )
    stripe_transfer_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text='Stripe Transfer id (Connect) or payout reference for community_amount',
    )
    paystack_transfer_reference = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text='Paystack transfer reference when community_amount is paid out via Paystack',
    )
    community_wallet = models.ForeignKey(
        CommunityWallet,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payment_transactions',
        help_text='Community wallet used when transferring community_amount (audit trail)',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True, help_text='When the payment was completed')

    class Meta:
        db_table = 'PaymentTransaction'
        verbose_name = 'Payment Transaction'
        verbose_name_plural = 'Payment Transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['app_subscription', 'status']),
            models.Index(fields=['community_member_subscription', 'status']),
            models.Index(fields=['store_purchase', 'status']),
            models.Index(fields=['event_registration', 'status']),
            models.Index(fields=['stripe_payment_intent_id']),
            models.Index(fields=['payment_gateway']),
            models.Index(fields=['transferred_to_community']),
        ]

    def __str__(self):
        if self.app_subscription:
            return f"App Subscription - ${self.total_amount} - {self.status}"
        if self.community_member_subscription:
            return f"{self.community_member_subscription.user.email} - ${self.total_amount} - {self.status}"
        if self.store_purchase:
            return f"Store {self.store_purchase.buyer_email} - ${self.total_amount} - {self.status}"
        if self.event_registration:
            return f"Event registration {self.event_registration_id} - ${self.total_amount} - {self.status}"
        return f"Transaction - ${self.total_amount} - {self.status}"
