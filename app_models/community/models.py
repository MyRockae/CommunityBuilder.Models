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

class CommunityGroup(models.Model):
    """
    Access tier for a community (formerly PaymentPlan).
    Whether the tier is free or paid is determined by CommunityGroupPrice rows: a tier is free when it has
    no price row with amount > 0 (or no rows at all). Gateway-specific amounts live on CommunityGroupPrice.

    For paid tiers, billing cadence is exactly one of: monthly, yearly, or lifetime (one payment, access until
    cancelled; no further charges). Recurring renewal must be implemented at the payment layer.
    """
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='community_groups')
    name = models.CharField(max_length=255, help_text='Name of the group tier (e.g., "Standard", "Premium", "Enterprise")')
    description = models.TextField(blank=True, null=True, help_text='Description of what this tier offers')
    is_monthly = models.BooleanField(
        default=False,
        help_text='Member is charged each billing month (recurring; payment service must enforce)',
    )
    is_yearly = models.BooleanField(
        default=False,
        help_text='Member is charged each billing year (recurring; payment service must enforce)',
    )
    is_lifetime = models.BooleanField(
        default=False,
        help_text='One purchase: no further charges; access does not expire by period (expires_at null)',
    )
    offerings = models.JSONField(default=dict, blank=True, help_text='JSON field to store tier offerings/features')
    is_active = models.BooleanField(default=True, help_text='Whether this tier is currently active and available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'CommunityGroup'
        verbose_name = 'Community Group'
        verbose_name_plural = 'Community Groups'
        unique_together = ['community', 'name']
        ordering = ['created_at']

    def clean(self):
        from django.core.exceptions import ValidationError

        flags = sum(bool(x) for x in (self.is_monthly, self.is_yearly, self.is_lifetime))
        if flags > 1:
            raise ValidationError('Set at most one of is_monthly, is_yearly, is_lifetime.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.community.name}"


class CommunityGroupPrice(models.Model):
    """
    List price for a community group (paid tier) in one ISO 4217 currency.
    Used for gateway-aware checkout (e.g. USD/Stripe vs NGN/Paystack), mirroring AppSubscriptionTierPrice.
    """

    community_group = models.ForeignKey(
        CommunityGroup,
        on_delete=models.CASCADE,
        related_name='prices',
        help_text='Community group tier this price applies to',
    )
    currency = models.CharField(
        max_length=3,
        help_text='ISO 4217 code (e.g. USD, NGN, GHS, ZAR)',
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Fee in major units of this currency',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'CommunityGroupPrice'
        verbose_name = 'Community group price'
        verbose_name_plural = 'Community group prices'
        constraints = [
            models.UniqueConstraint(
                fields=['community_group', 'currency'],
                name='commgroupprice_unique_group_currency',
            ),
        ]

    def __str__(self):
        return f'{self.community_group_id} {self.currency} {self.amount}'


class CommunityGroupAccess(models.Model):
    """
    Which user has access to which community tier (formerly UserPaymentPlan).
    For paid communities, billing truth is CommunityMemberSubscription; keep dates in sync via API.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_group_accesses')
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='community_group_access_entries')
    community_group = models.ForeignKey(CommunityGroup, on_delete=models.CASCADE, related_name='access_assignments')
    subscribed_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text='When access expires (null for lifetime)')
    is_active = models.BooleanField(default=True, help_text='Whether this access is currently active')

    class Meta:
        db_table = 'CommunityGroupAccess'
        verbose_name = 'Community Group Access'
        verbose_name_plural = 'Community Group Access'
        unique_together = ['user', 'community', 'community_group']
        ordering = ['-subscribed_at']

    def __str__(self):
        return f"{self.user.email} - {self.community_group.name} ({self.community.name})"

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
def create_default_community_group(sender, instance, created, **kwargs):
    """Create a default free 'hobby plan' tier when a community is created"""
    if created:
        CommunityGroup.objects.create(
            community=instance,
            name='hobby plan',
            description='Default free tier for the community',
            is_monthly=False,
            is_yearly=False,
            is_lifetime=True,
            is_active=True,
        )
