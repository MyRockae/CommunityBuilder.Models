from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import slugify
from app_models.account.models import User
from app_models.shared.models import Tag
from app_models.shared.validators import slug_username_validator


def _current_year():
    return timezone.now().year


class Community(models.Model):
    name = models.CharField(max_length=255)
    alias = models.SlugField(
        max_length=255,
        unique=True,
        db_index=True,
        validators=[slug_username_validator],
        help_text='Unique URL-friendly identifier. Only letters, numbers, hyphens (-) and underscores (_) allowed.',
    )
    summary = models.CharField(max_length=500, blank=True, null=True, help_text='Short summary of the community')
    description = models.TextField(blank=True, null=True)
    public_notes = models.TextField(blank=True, null=True, help_text='Public notes visible to all community members and visitors')
    category = models.CharField(max_length=100, blank=True, null=True, help_text='Community category')
    is_open = models.BooleanField(default=True, help_text='If true, users can join without approval. If false, users become applicants needing approval.')
    restrict_posting_to_owners_moderators = models.BooleanField(default=False, help_text='If true, only owners and moderators can post on the community forum. If false, all members can post.')
    use_logo_only = models.BooleanField(default=False, help_text='If true, the community should be represented only by its logo/avatar without showing the name text. If false, display both logo and name. This is for frontend display purposes.')
    avatar_url = models.URLField(blank=True, null=True)
    banner_url = models.URLField(blank=True, null=True)
    tags = models.ManyToManyField(Tag, related_name='communities', blank=True)
    is_active = models.BooleanField(default=True, help_text='If false, the community is hidden or disabled.')
    flag_count = models.PositiveIntegerField(default=0, help_text='Number of times the community has been flagged by users.')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    members = models.ManyToManyField(User, through='CommunityMember', through_fields=('community', 'user'), related_name='communities')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Generate alias from name if not provided
        if not self.alias:
            base_alias = slugify(self.name)
            # Ensure uniqueness
            alias = base_alias
            counter = 1
            while Community.objects.filter(alias=alias).exists():
                alias = f"{base_alias}-{counter}"
                counter += 1
            self.alias = alias
        
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'Community'
        verbose_name = 'Community'
        verbose_name_plural = 'Communities'
        ordering = ['-created_at']

class CommunityMember(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('co_owner', 'Co-Owner'),
        ('moderator', 'Moderator'),
        ('contributor', 'Contributor'),
        ('member', 'Member'),
        ('applicant', 'Applicant'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_memberships')
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='community_members')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='applicant')
    joined_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='approved_memberships',
        help_text='User who approved this membership (for applicants)'
    )
    is_blocked = models.BooleanField(default=False, help_text='Whether the user is blocked from the community')
    blocked_at = models.DateTimeField(null=True, blank=True)
    blocked_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='blocked_memberships',
        help_text='User who blocked this member'
    )
    points = models.PositiveBigIntegerField(default=0, help_text='Cumulative points for community leaderboard')
    leaderboard_year = models.PositiveSmallIntegerField(
        default=_current_year,
        help_text='Year this leaderboard period applies to; points reset when year changes.',
    )

    class Meta:
        db_table = 'CommunityMember'
        verbose_name = 'Community Member'
        verbose_name_plural = 'Community Members'
        unique_together = ['user', 'community']
        ordering = ['-joined_at']

    def clean(self):
        """Validate that only one owner exists per community"""
        from django.core.exceptions import ValidationError
        
        # Only check if this is being set to owner
        if self.role == 'owner':
            # Check if there's already an owner in this community (excluding this instance)
            existing_owner = CommunityMember.objects.filter(
                community=self.community,
                role='owner'
            ).exclude(pk=self.pk if self.pk else None).first()
            
            if existing_owner:
                raise ValidationError(
                    f"A community can only have one owner. {existing_owner.user.email} is already the owner."
                )
    
    def save(self, *args, **kwargs):
        """Override save to call clean validation"""
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} - {self.community.name} ({self.get_role_display()})"

class CommunityLike(models.Model):
    """Model to track user likes on communities"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_likes')
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'CommunityLike'
        verbose_name = 'Community Like'
        verbose_name_plural = 'Community Likes'
        unique_together = ['user', 'community']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} liked {self.community.name}"


class CommunityView(models.Model):
    """Model to track community views (who viewed, when). User is nullable for anonymous views."""
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name='community_views',
        help_text='Community that was viewed',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='community_views',
        null=True,
        blank=True,
        help_text='User who viewed; null for anonymous views.',
    )
    viewed_at = models.DateTimeField(auto_now_add=True, help_text='When the view was recorded')
    referrer_url = models.URLField(max_length=2048, blank=True, null=True, help_text='URL of the referring page')
    referrer_domain = models.CharField(max_length=255, blank=True, null=True, help_text='Domain of the referrer')
    country = models.CharField(max_length=100, blank=True, null=True, help_text='Country of the viewer')
    region = models.CharField(max_length=100, blank=True, null=True, help_text='Region/state of the viewer')
    city = models.CharField(max_length=100, blank=True, null=True, help_text='City of the viewer')

    class Meta:
        db_table = 'CommunityView'
        verbose_name = 'Community View'
        verbose_name_plural = 'Community Views'
        ordering = ['-viewed_at']

    def __str__(self):
        viewer = self.user.email if self.user else 'anonymous'
        return f"{viewer} viewed {self.community.name} at {self.viewed_at}"

class PaymentPlan(models.Model):
    """Payment plan model for communities"""
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='payment_plans')
    name = models.CharField(max_length=255, help_text='Name of the payment plan (e.g., "Standard", "Premium", "Enterprise")')
    description = models.TextField(blank=True, null=True, help_text='Description of what this plan offers')
    fee = models.DecimalField(max_digits=10, decimal_places=2, help_text='Subscription fee for this plan')
    is_recurring = models.BooleanField(default=False, help_text='Whether this payment plan is recurring (subscription-based)')
    is_free = models.BooleanField(default=False, help_text='Whether this plan is free. If True, fee will be automatically set to 0 and is_recurring will be False.')
    offerings = models.JSONField(default=dict, blank=True, help_text='JSON field to store plan offerings/features')
    is_active = models.BooleanField(default=True, help_text='Whether this plan is currently active and available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'PaymentPlan'
        verbose_name = 'Payment Plan'
        verbose_name_plural = 'Payment Plans'
        unique_together = ['community', 'name']
        ordering = ['created_at']
    
    def clean(self):
        """Validate that is_free=True sets fee=0 and is_recurring=False"""
        from django.core.exceptions import ValidationError
        if self.is_free:
            self.fee = 0
            self.is_recurring = False
    
    def save(self, *args, **kwargs):
        """Override save to ensure is_free logic is applied"""
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} - {self.community.name}"

class UserPaymentPlan(models.Model):
    """Model to track which payment plan a user is subscribed to"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_payment_plans')
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='user_subscriptions')
    payment_plan = models.ForeignKey(PaymentPlan, on_delete=models.CASCADE, related_name='subscribers')
    subscribed_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text='When the subscription expires (null for lifetime)')
    is_active = models.BooleanField(default=True, help_text='Whether this subscription is currently active')
    
    class Meta:
        db_table = 'UserPaymentPlan'
        verbose_name = 'User Payment Plan'
        verbose_name_plural = 'User Payment Plans'
        unique_together = ['user', 'community']
        ordering = ['-subscribed_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.payment_plan.name} ({self.community.name})"

class CommunityBadgeDefinition(models.Model):
    """
    Community-level badge definition. e.g. first_post, posts_5, post_likes_100.
    """
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name='badge_definitions',
        help_text='Community this badge belongs to',
    )
    code = models.CharField(
        max_length=64,
        help_text='Unique code within the community (e.g. first_post, posts_5, post_likes_100)',
    )
    name = models.CharField(max_length=255, help_text='Display name of the badge')
    description = models.TextField(blank=True, null=True, help_text='Short description of how to earn this badge')
    icon_url = models.URLField(
        blank=True,
        null=True,
        help_text='URL of the badge icon image (optional)',
    )
    criteria = models.JSONField(
        default=dict,
        blank=True,
        help_text='Optional criteria (e.g. {"min_posts": 5})',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'CommunityBadgeDefinition'
        verbose_name = 'Community Badge Definition'
        verbose_name_plural = 'Community Badge Definitions'
        unique_together = ['community', 'code']
        ordering = ['community', 'code']

    def __str__(self):
        return f"{self.name} ({self.code}) - {self.community.name}"


class CommunityMemberBadge(models.Model):
    """
    Links a community member to a community-level badge they have been awarded.
    """
    community_member = models.ForeignKey(
        CommunityMember,
        on_delete=models.CASCADE,
        related_name='badges',
        help_text='Community member who was awarded this badge',
    )
    community_badge = models.ForeignKey(
        CommunityBadgeDefinition,
        on_delete=models.CASCADE,
        related_name='member_badges',
        help_text='The community badge that was awarded',
    )
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'CommunityMemberBadge'
        verbose_name = 'Community Member Badge'
        verbose_name_plural = 'Community Member Badges'
        unique_together = ['community_member', 'community_badge']
        ordering = ['-awarded_at']

    def __str__(self):
        return f"{self.community_member.user.email} - {self.community_badge.code} ({self.community_member.community.name})"


# Signal to create default "hobby plan" when a community is created
@receiver(post_save, sender=Community)
def create_default_payment_plan(sender, instance, created, **kwargs):
    """Create a default 'hobby plan' payment plan when a community is created"""
    if created:
        PaymentPlan.objects.create(
            community=instance,
            name='hobby plan',
            description='Default free plan for the community',
            fee=0,
            is_recurring=False,
            is_free=True,
            is_active=True
        )
