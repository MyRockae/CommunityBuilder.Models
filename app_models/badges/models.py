from django.db import models
from app_models.account.models import User


class BadgeDefinition(models.Model):
    """
    App-level badge definition (platform-wide). e.g. signup, referral, early_adopter_1000.
    """
    code = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        help_text='Unique code/slug for this badge (e.g. signup, referral, early_adopter_1000)',
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
        help_text='Optional criteria (e.g. {"max_rank": 1000} for early adopter)',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'BadgeDefinition'
        verbose_name = 'Badge Definition'
        verbose_name_plural = 'Badge Definitions'
        ordering = ['code']

    def __str__(self):
        return f"{self.name} ({self.code})"


class UserBadge(models.Model):
    """
    Links a user to an app-level badge they have been awarded.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='badges',
        help_text='User who was awarded this badge',
    )
    badge = models.ForeignKey(
        BadgeDefinition,
        on_delete=models.CASCADE,
        related_name='user_badges',
        help_text='The badge that was awarded',
    )
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'UserBadge'
        verbose_name = 'User Badge'
        verbose_name_plural = 'User Badges'
        unique_together = ['user', 'badge']
        ordering = ['-awarded_at']

    def __str__(self):
        return f"{self.user.email} - {self.badge.code}"
