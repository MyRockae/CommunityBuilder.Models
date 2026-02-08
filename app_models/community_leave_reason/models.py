from django.db import models
from app_models.account.models import User
from app_models.community.models import Community


class CommunityLeaveReason(models.Model):
    """
    Record of why a user left a community, with their contact info.
    Collected when they leave (leave community flow). One record per leave event.
    """
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name='leave_reasons',
        help_text='Community the user left',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='community_leave_reasons',
        help_text='User who left (if authenticated)',
    )
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    middle_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField()
    phone_number = models.CharField(max_length=50, blank=True)
    reason = models.TextField(help_text='Reason for leaving the community')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'CommunityLeaveReason'
        verbose_name = 'Community Leave Reason'
        verbose_name_plural = 'Community Leave Reasons'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['community']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.email} – left {self.community.name} at {self.created_at}"
