from django.db import models
from django.utils import timezone
from decimal import Decimal
from app_models.account.models import User
from app_models.community.models import Community, CommunityGroup


class PaymentGateway(models.TextChoices):
    STRIPE = 'stripe', 'Stripe'
    PAYSTACK = 'paystack', 'Paystack'


class AppSubscriptionTier(models.Model):
    """App subscription tier definitions (Free/Hobby, Hobby, Professional, Enterprise)"""
    TIER_CHOICES = [
        ('free_hobby', 'Free/Hobby (Starter)'),
        ('hobby', 'Hobby (Growing)'),
        ('professional', 'Professional (Established)'),
        ('enterprise', 'Enterprise (Scale)'),
    ]
    
    tier_name = models.CharField(max_length=50, choices=TIER_CHOICES, unique=True, help_text='Tier identifier')
    display_name = models.CharField(max_length=255, help_text='Display name for the tier')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Monthly price')
    
    # Limits
    max_communities = models.IntegerField(null=True, blank=True, help_text='Maximum number of communities (null = unlimited)')
    max_members = models.IntegerField(null=True, blank=True, help_text='Maximum members per community (null = unlimited)')
    max_admins = models.IntegerField(null=True, blank=True, help_text='Maximum admins (co-owners + moderators) per community (null = unlimited)')
    max_free_community_groups = models.IntegerField(null=True, blank=True, help_text='Maximum free community groups (tiers) per community (null = unlimited)')
    max_paid_community_groups = models.IntegerField(null=True, blank=True, help_text='Maximum paid community groups (tiers) per community (null = unlimited)')
    max_quiz_generations_per_month = models.IntegerField(null=True, blank=True, help_text='Maximum quiz generations per month (null = unlimited)')
    max_forums = models.IntegerField(null=True, blank=True, help_text='Maximum forums per community (null = unlimited)')
    max_classrooms = models.IntegerField(null=True, blank=True, help_text='Maximum classrooms per community (null = unlimited)')
    storage_limit_gb = models.IntegerField(null=True, blank=True, help_text='Storage limit in GB per owner (null = unlimited)')
    
    # Features (boolean flags)
    has_basic_analytics = models.BooleanField(default=False)
    has_advanced_analytics = models.BooleanField(default=False)
    has_custom_reports = models.BooleanField(default=False)
    has_standard_support = models.BooleanField(default=False)
    has_priority_support = models.BooleanField(default=False)
    has_24_7_support = models.BooleanField(default=False)
    has_custom_branding = models.BooleanField(default=False)
    has_white_label = models.BooleanField(default=False)
    has_meeting_features = models.BooleanField(default=False)
    has_advanced_meeting_features = models.BooleanField(default=False)
    has_export_data = models.BooleanField(default=False)
    has_api_access = models.BooleanField(default=False)
    has_custom_integrations = models.BooleanField(default=False)
    has_revenue_analytics = models.BooleanField(default=False)
    has_dedicated_manager = models.BooleanField(default=False)
    has_custom_development = models.BooleanField(default=False)
    has_sso_saml = models.BooleanField(default=False)
    has_advanced_security = models.BooleanField(default=False)
    has_custom_sla = models.BooleanField(default=False)
    has_multi_community_dashboard = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'AppSubscriptionTier'
        verbose_name = 'App Subscription Tier'
        verbose_name_plural = 'App Subscription Tiers'
        ordering = ['price']
    
    def __str__(self):
        return f"{self.display_name} (${self.price}/month)"


class AppSubscription(models.Model):
    """Owner's subscription to the app platform"""
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='app_subscriptions', help_text='Community owner')
    tier = models.ForeignKey(AppSubscriptionTier, on_delete=models.PROTECT, related_name='subscriptions', help_text='Subscription tier')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    subscribed_at = models.DateTimeField(auto_now_add=True)
    activated_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    # Stripe fields (will be managed by payment API)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)

    # Billing snapshot & gateway (set when checkout is created or confirmed)
    billing_country = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        help_text='ISO 3166-1 alpha-2 country used for this subscription checkout',
    )
    payment_gateway = models.CharField(
        max_length=20,
        choices=PaymentGateway.choices,
        blank=True,
        null=True,
        help_text='Payment processor handling this subscription',
    )
    # Paystack (parallel to Stripe ids above)
    paystack_customer_code = models.CharField(max_length=255, blank=True, null=True)
    paystack_subscription_code = models.CharField(max_length=255, blank=True, null=True)
    paystack_transaction_reference = models.CharField(max_length=255, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'AppSubscription'
        verbose_name = 'App Subscription'
        verbose_name_plural = 'App Subscriptions'
        ordering = ['-subscribed_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'expires_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.tier.display_name} - {self.status}"
    
    def is_active(self):
        """Check if subscription is currently active"""
        if self.status != 'active':
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return True


class StorageUsage(models.Model):
    """Track storage usage per file for subscription limit enforcement"""
    FILE_TYPE_CHOICES = [
        ('avatar', 'Avatar'),
        ('banner', 'Banner'),
        ('classroom_content', 'Classroom Content'),
        ('classroom_attachment', 'Classroom Attachment'),
        ('forum_attachment', 'Forum Attachment'),
        ('post_attachment', 'Post Attachment'),
        ('quiz_file', 'Quiz File'),
        ('blog_image', 'Blog Image'),
        ('featured_content', 'Featured Content'),
        ('other', 'Other'),
    ]
    
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='storage_usage', null=True, blank=True, help_text='Community this file belongs to (null for user profile files)')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='storage_usage', help_text='Community owner (for per-owner storage limits)')
    file_path = models.CharField(max_length=500, help_text='MinIO object path')
    file_size = models.BigIntegerField(help_text='File size in bytes')
    file_type = models.CharField(max_length=50, choices=FILE_TYPE_CHOICES, default='other')
    parent_entity_type = models.CharField(max_length=100, null=True, blank=True, help_text='Type of parent entity (e.g. Classroom, Post)')
    parent_entity_id = models.PositiveBigIntegerField(null=True, blank=True, help_text='ID of the parent entity')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'StorageUsage'
        verbose_name = 'Storage Usage'
        verbose_name_plural = 'Storage Usage'
        indexes = [
            models.Index(fields=['owner']),
            models.Index(fields=['community', 'owner']),
            models.Index(fields=['file_path']),
        ]
    
    def __str__(self):
        return f"{self.owner.email} - {self.file_path} - {self.file_size} bytes"


class CommunityMemberSubscription(models.Model):
    """Billing record per member/community/tier (member → owner, with 2% platform fee). Multiple rows per member per community are allowed when they pay for different community_groups."""
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]
    
    # Foreign keys to models (shared database)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_member_subscriptions', help_text='Member who has the subscription')
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='member_subscriptions', help_text='Community this subscription is for')
    community_group = models.ForeignKey(CommunityGroup, on_delete=models.CASCADE, related_name='member_subscriptions', help_text='Community group (tier) the member is subscribed to')
    
    # Subscription details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', help_text='Current status of the subscription')
    subscribed_at = models.DateTimeField(auto_now_add=True, help_text='When the subscription was created')
    activated_at = models.DateTimeField(null=True, blank=True, help_text='When the subscription was activated (payment confirmed)')
    expires_at = models.DateTimeField(null=True, blank=True, help_text='When the subscription expires (for recurring plans)')
    cancelled_at = models.DateTimeField(null=True, blank=True, help_text='When the subscription was cancelled')
    
    # Stripe integration fields
    stripe_subscription_id = models.CharField(max_length=255, null=True, blank=True, help_text='Stripe subscription ID (for recurring subscriptions)')
    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True, help_text='Stripe customer ID')
    stripe_payment_intent_id = models.CharField(max_length=255, null=True, blank=True, help_text='Stripe payment intent ID (for one-time payments)')

    billing_country = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        help_text='ISO 3166-1 alpha-2 country for this member subscription checkout',
    )
    payment_gateway = models.CharField(
        max_length=20,
        choices=PaymentGateway.choices,
        blank=True,
        null=True,
        help_text='Payment processor handling this subscription',
    )
    paystack_customer_code = models.CharField(max_length=255, blank=True, null=True)
    paystack_subscription_code = models.CharField(max_length=255, blank=True, null=True)
    paystack_transaction_reference = models.CharField(max_length=255, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'CommunityMemberSubscription'
        verbose_name = 'Community Member Subscription'
        verbose_name_plural = 'Community Member Subscriptions'
        unique_together = ['user', 'community', 'community_group']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'community', 'status']),
            models.Index(fields=['status', 'expires_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.community.name} - {self.community_group.name}"
    
    def is_active(self):
        """Check if subscription is currently active"""
        if self.status != 'active':
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return True
    
    def days_until_expiry(self):
        """Calculate days until subscription expires"""
        if not self.expires_at:
            return None
        delta = self.expires_at - timezone.now()
        return max(0, delta.days)


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
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    # Transaction type and related record (exactly one should be set for a given charge)
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPE_CHOICES, help_text='Type of transaction')
    app_subscription = models.ForeignKey(AppSubscription, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True, help_text='App subscription (if transaction_type is app_subscription)')
    community_member_subscription = models.ForeignKey(CommunityMemberSubscription, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True, help_text='Community member subscription (if transaction_type is community_member_subscription)')
    store_purchase = models.ForeignKey(
        'community_store.StorePurchase',
        on_delete=models.CASCADE,
        related_name='payment_transactions',
        null=True,
        blank=True,
        help_text='Store product purchase (if transaction_type is store_purchase)',
    )
    
    # Payment amounts
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
    
    # Stripe fields
    stripe_payment_intent_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        help_text='Stripe PaymentIntent id (null when payment_gateway is paystack)',
    )
    stripe_charge_id = models.CharField(max_length=255, null=True, blank=True, help_text='Stripe charge ID')
    
    # Paystack fields
    paystack_transaction_reference = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        help_text='Paystack transaction reference (null when payment_gateway is stripe)',
    )
    
    # Transfer tracking (community member subscriptions and store purchases — batch e.g. weekly)
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
        'CreatorPayoutAccount',
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
        return f"Transaction - ${self.total_amount} - {self.status}"


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

    # Stripe Connect (when payment_gateway is stripe)
    stripe_connect_account_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Stripe Connect account id (acct_…)',
    )

    # Paystack (when payment_gateway is paystack)
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
