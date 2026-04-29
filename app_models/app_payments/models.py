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


class CreatorPayoutAccount(models.Model):
    """
    A creator (community owner) can attach multiple payout destinations over time
    (e.g. Stripe Connect for UK/US/CA and Paystack subaccount/recipient for Nigeria).
    Payment service picks the row that matches buyer gateway/currency and is_primary when needed.
    """
    STATUS_PENDING = 'pending'
    STATUS_ACTIVE = 'active'
    STATUS_RESTRICTED = 'restricted'
    STATUS_DISABLED = 'disabled'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending onboarding'),
        (STATUS_ACTIVE, 'Active — payouts enabled'),
        (STATUS_RESTRICTED, 'Restricted'),
        (STATUS_DISABLED, 'Disabled'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='creator_payout_accounts',
        help_text='Creator (community owner) receiving payouts',
    )
    payment_gateway = models.CharField(
        max_length=20,
        choices=PaymentGateway.choices,
        help_text='Processor this payout account is registered with',
    )
    label = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text='Optional label shown to the creator (e.g. main bank, NGN wallet)',
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        help_text='Onboarding / capability state mirrored from the gateway where possible',
    )
    is_primary = models.BooleanField(
        default=False,
        help_text='Preferred account for this user on this gateway (splits / transfers)',
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
        db_table = 'CreatorPayoutAccount'
        verbose_name = 'Creator payout account'
        verbose_name_plural = 'Creator payout accounts'
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
                condition=models.Q(is_primary=True),
                name='creatorpayoutaccount_unique_primary_per_user_gateway',
            ),
        ]

    def __str__(self):
        return f'{self.user.email} — {self.payment_gateway} ({self.status})'


class PayoutProfile(models.Model):
    """Per-user payout preferences (one row per user)."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='payout_profile',
        help_text='User this payout profile belongs to',
    )
    preferred_payment_gateway = models.CharField(
        max_length=20,
        choices=PaymentGateway.choices,
        blank=True,
        null=True,
        help_text='Preferred processor for payouts when the user has multiple options',
    )
    legal_full_name = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text='Legal name as shown on tax or bank documents',
    )
    tax_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Hashed tax identifier (e.g. EIN, VAT); never store plaintext',
    )
    identity_document_number = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Hashed government ID number for KYC; never store plaintext',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'PayoutProfile'
        verbose_name = 'Payout profile'
        verbose_name_plural = 'Payout profiles'

    def __str__(self):
        gw = self.preferred_payment_gateway or '—'
        return f'{self.user.email} — preferred: {gw}'


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
        help_text='Buyer who may redeem this session (must match authenticated user on exchange)',
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

    For community-linked payments, use platform_fee / owner_amount and transferred_to_owner /
    stripe_transfer_id or paystack_transfer_reference the same way: collect on the platform account,
    then pay the community owner on your schedule (e.g. weekly batch).
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
        on_delete=models.CASCADE,
        related_name='payment_transactions',
        null=True,
        blank=True,
        help_text='Event registration (if transaction_type is event_registration)',
    )

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text='Total payment amount charged to the buyer')
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Platform cut (e.g. 2% for community subscriptions and store sales; 0 for app subscriptions)')
    owner_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Amount owed to the community owner after platform_fee (e.g. 98% for member subs and store sales)')

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

    transferred_to_owner = models.BooleanField(default=False, help_text='Whether owner_amount has been paid out to the community owner')
    transferred_at = models.DateTimeField(null=True, blank=True, help_text='When the transfer to owner was completed')
    stripe_transfer_id = models.CharField(max_length=255, null=True, blank=True, help_text='Stripe Transfer id (Connect) or payout reference for owner_amount')
    paystack_transfer_reference = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text='Paystack transfer reference when owner_amount is paid out via Paystack',
    )
    creator_payout_account = models.ForeignKey(
        CreatorPayoutAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payment_transactions',
        help_text='Creator payout profile used when transferring owner_amount (audit trail)',
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
            models.Index(fields=['transferred_to_owner']),
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
