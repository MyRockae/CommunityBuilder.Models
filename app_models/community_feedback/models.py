from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from app_models.account.models import User
from app_models.community.models import Community


class CommunityFeedback(models.Model):
    """
    User feedback for a community: star rating (1–5) and optional message.
    One feedback per user per community; users can update their feedback.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='community_feedbacks',
        help_text='User who left the feedback',
    )
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name='feedbacks',
        help_text='Community this feedback is for',
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Star rating from 1 to 5',
    )
    message = models.TextField(
        blank=True,
        null=True,
        help_text='Optional feedback message',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'CommunityFeedback'
        verbose_name = 'Community Feedback'
        verbose_name_plural = 'Community Feedbacks'
        unique_together = ['user', 'community']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['community']),
            models.Index(fields=['user', 'community']),
        ]

    def __str__(self):
        return f"{self.user.email} – {self.community.name} ({self.rating} stars)"
