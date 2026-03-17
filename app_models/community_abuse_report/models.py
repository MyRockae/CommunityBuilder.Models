from django.db import models
from app_models.account.models import User
from app_models.community.models import Community


class CommunityAbuseReport(models.Model):
    """User abuse/violation report for a community. Links community, reporter, and message."""
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name='reports',
        help_text='Community that was reported',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='community_reports',
        help_text='User who reported the community',
    )
    message = models.TextField(help_text='Report reason or description')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'CommunityAbuseReport'
        verbose_name = 'Community Abuse Report'
        verbose_name_plural = 'Community Abuse Reports'
        ordering = ['-created_at']

    def __str__(self):
        return f"Abuse report by {self.user.email} on {self.community.name}"
