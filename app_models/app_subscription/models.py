from django.db import models
from django.utils import timezone
from decimal import Decimal
from app_models.account.models import User
from app_models.community.models import Community, PaymentPlan


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
    max_free_payment_plans = models.IntegerField(null=True, blank=True, help_text='Maximum free payment plans per community (null = unlimited)')
    max_paid_payment_plans = models.IntegerField(null=True, blank=True, help_text='Maximum paid payment plans per community (null = unlimited)')
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
    """Community member subscription: Member subscribes to community payment plan (member → owner, with 2% platform fee)"""
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]
    
    # Foreign keys to models (shared database)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_member_subscriptions', help_text='Member who has the subscription')
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='member_subscriptions', help_text='Community this subscription is for')
    payment_plan = models.ForeignKey(PaymentPlan, on_delete=models.CASCADE, related_name='member_subscriptions', help_text='Payment plan user is subscribed to')
    
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
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'CommunityMemberSubscription'
        verbose_name = 'Community Member Subscription'
        verbose_name_plural = 'Community Member Subscriptions'
        unique_together = ['user', 'community']  # One subscription per user per community
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'community', 'status']),
            models.Index(fields=['status', 'expires_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.community.name} - {self.payment_plan.name}"
    
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
    """Model to track payment transactions for both app and community member subscriptions"""
    TRANSACTION_TYPE_CHOICES = [
        ('app_subscription', 'App Subscription'),
        ('community_member_subscription', 'Community Member Subscription'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    # Transaction type and related subscription
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPE_CHOICES, help_text='Type of transaction')
    app_subscription = models.ForeignKey(AppSubscription, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True, help_text='App subscription (if transaction_type is app_subscription)')
    community_member_subscription = models.ForeignKey(CommunityMemberSubscription, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True, help_text='Community member subscription (if transaction_type is community_member_subscription)')
    
    # Payment amounts
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text='Total payment amount (100% of fee)')
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Platform fee (2% for community subscriptions, 0 for app subscriptions)')
    owner_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Amount to owner (98% for community subscriptions, 0 for app subscriptions)')
    
    currency = models.CharField(max_length=3, default='USD', help_text='Currency code (USD, EUR, etc.)')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', help_text='Payment status')
    
    # Stripe fields
    stripe_payment_intent_id = models.CharField(max_length=255, unique=True, help_text='Stripe payment intent ID')
    stripe_charge_id = models.CharField(max_length=255, null=True, blank=True, help_text='Stripe charge ID')
    
    # Transfer tracking (for community member subscriptions - manual transfer to owner)
    transferred_to_owner = models.BooleanField(default=False, help_text='Whether the owner amount has been transferred to the community owner')
    transferred_at = models.DateTimeField(null=True, blank=True, help_text='When the transfer to owner was completed')
    stripe_transfer_id = models.CharField(max_length=255, null=True, blank=True, help_text='Stripe transfer ID (if using Stripe Connect)')
    
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
            models.Index(fields=['stripe_payment_intent_id']),
            models.Index(fields=['transferred_to_owner']),
        ]
    
    def __str__(self):
        if self.app_subscription:
            return f"App Subscription - ${self.total_amount} - {self.status}"
        elif self.community_member_subscription:
            return f"{self.community_member_subscription.user.email} - ${self.total_amount} - {self.status}"
        return f"Transaction - ${self.total_amount} - {self.status}"
