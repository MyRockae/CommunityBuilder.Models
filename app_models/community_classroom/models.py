from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from app_models.account.models import User
from app_models.community.models import Community, CommunityGroup
from app_models.shared.validators import slug_username_validator

class Classroom(models.Model):
    """Classroom model for community - contains name, title, description, and banner"""
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='classrooms')
    name = models.CharField(
        max_length=255,
        validators=[slug_username_validator],
        help_text='Name of the classroom. Only letters, numbers, hyphens (-) and underscores (_) allowed.',
    )
    title = models.CharField(max_length=255, help_text='Title of the classroom')
    description = models.TextField(blank=True, null=True, help_text='Description of the classroom')
    banner_url = models.URLField(blank=True, null=True, help_text='URL of the classroom banner image')
    community_groups = models.ManyToManyField(CommunityGroup, related_name='classrooms', blank=True, help_text='Community groups (tiers) that have access to this classroom')
    enforce_progression = models.BooleanField(default=False, help_text='If True, users must complete content in order (one at a time). Owners/moderators can view all content regardless.')
    issue_certificate = models.BooleanField(default=False, help_text='If True, users will receive a certificate when all content in the classroom is completed')
    is_featured = models.BooleanField(
        default=False,
        help_text='If True, the classroom may be highlighted in discovery; at most six per community may be featured.',
    )
    is_published = models.BooleanField(default=False, help_text='If True, the classroom is visible/published to members')
    published_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Set once when the classroom is first published; remains set if is_published is toggled off so downstream notifications fire only once.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'Classroom'
        verbose_name = 'Classroom'
        verbose_name_plural = 'Classrooms'
        unique_together = ['community', 'name']  # Each community can have unique classroom names
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        update_fields = kwargs.get('update_fields')
        if self.is_published and self.published_at is None:
            self.published_at = timezone.now()
            if update_fields is not None:
                kwargs['update_fields'] = list({*update_fields, 'published_at'})
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.community.name}"


class ClassroomReview(models.Model):
    """
    Member review for a classroom: star rating (1–5) and optional message.
    One review per user per classroom; users can update their review.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='classroom_reviews',
        help_text='User who left the review',
    )
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text='Classroom this review is for',
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Star rating from 1 to 5',
    )
    message = models.TextField(
        blank=True,
        null=True,
        help_text='Optional review message',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ClassroomReview'
        verbose_name = 'Classroom Review'
        verbose_name_plural = 'Classroom Reviews'
        unique_together = ['user', 'classroom']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['classroom']),
            models.Index(fields=['user', 'classroom']),
        ]

    def __str__(self):
        return f"{self.user.email} – {self.classroom.title} ({self.rating} stars)"
