from django.db import models
from django.utils import timezone
from app_models.account.models import User
from app_models.app_payments.models import PaymentGateway
from app_models.community.models import Community, CommunityGroup


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
        ordering = ['tier_name']

    def __str__(self):
        return f'{self.display_name} ({self.tier_name})'


class AppSubscriptionTierPrice(models.Model):
    """List price for an app tier in one ISO 4217 currency (USD for Stripe, NGN/GHS/ZAR etc. for Paystack)."""

    tier = models.ForeignKey(
        AppSubscriptionTier,
        on_delete=models.CASCADE,
        related_name='prices',
        help_text='Subscription tier this price applies to',
    )
    currency = models.CharField(
        max_length=3,
        help_text='ISO 4217 code (e.g. USD, NGN, GHS, ZAR)',
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Price in major units of this currency',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'AppSubscriptionTierPrice'
        verbose_name = 'App subscription tier price'
        verbose_name_plural = 'App subscription tier prices'
        constraints = [
            models.UniqueConstraint(
                fields=['tier', 'currency'],
                name='appsubtierprice_unique_tier_currency',
            ),
        ]

    def __str__(self):
        return f'{self.tier.tier_name} {self.currency} {self.amount}'


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

    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)

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
        if self.status != 'active':
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return True


class CommunityMemberSubscription(models.Model):
    """Billing record per member/community/tier (member → owner, with 2% platform fee). Multiple rows per member per community are allowed when they pay for different community_groups."""
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_member_subscriptions', help_text='Member who has the subscription')
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='member_subscriptions', help_text='Community this subscription is for')
    community_group = models.ForeignKey(CommunityGroup, on_delete=models.CASCADE, related_name='member_subscriptions', help_text='Community group (tier) the member is subscribed to')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', help_text='Current status of the subscription')
    subscribed_at = models.DateTimeField(auto_now_add=True, help_text='When the subscription was created')
    activated_at = models.DateTimeField(null=True, blank=True, help_text='When the subscription was activated (payment confirmed)')
    expires_at = models.DateTimeField(null=True, blank=True, help_text='When the subscription expires (for recurring plans)')
    cancelled_at = models.DateTimeField(null=True, blank=True, help_text='When the subscription was cancelled')

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
        if self.status != 'active':
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return True

    def days_until_expiry(self):
        if not self.expires_at:
            return None
        delta = self.expires_at - timezone.now()
        return max(0, delta.days)

