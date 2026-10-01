from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from app_models.account.models import User
from app_models.community.models import Community, CommunityGroup
from app_models.shared.validators import slug_username_validator


class CoursePublicPreviewScope(models.TextChoices):
    NONE = 'none', 'None'
    ENTIRE = 'entire', 'Entire course'
    PARTS = 'parts', 'Selected lessons'


class Course(models.Model):
    """Course model for community - contains name, title, description, and banner"""
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='courses')
    name = models.CharField(
        max_length=255,
        validators=[slug_username_validator],
        help_text='Name of the course. Only letters, numbers, hyphens (-) and underscores (_) allowed.',
    )
    title = models.CharField(max_length=255, help_text='Title of the course')
    description = models.TextField(blank=True, null=True, help_text='Description of the course')
    banner_url = models.URLField(blank=True, null=True, help_text='URL of the course banner image')
    community_groups = models.ManyToManyField(CommunityGroup, related_name='courses', blank=True, help_text='Community groups (tiers) that have access to this course')
    enforce_progression = models.BooleanField(default=False, help_text='If True, users must complete content in order (one at a time). Owners/moderators can view all content regardless.')
    issue_certificate = models.BooleanField(default=False, help_text='If True, users will receive a certificate when all content in the course is completed')
    is_featured = models.BooleanField(
        default=False,
        help_text='If True, the course is listed on the public featured catalog.',
    )
    public_preview_scope = models.CharField(
        max_length=16,
        choices=CoursePublicPreviewScope.choices,
        default=CoursePublicPreviewScope.NONE,
        help_text=(
            'How guest preview lessons are chosen: none (not shown to visitors), '
            'entire (every syllabus row is public), or parts (selected rows only). '
            'New lessons inherit is_preview when this is entire.'
        ),
    )
    is_published = models.BooleanField(default=False, help_text='If True, the course is visible/published to members')
    published_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Set once when the course is first published; remains set if is_published is toggled off so downstream notifications fire only once.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'Course'
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        unique_together = ['community', 'name']  # Each community can have unique course names
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


class CourseReview(models.Model):
    """
    Member review for a course: star rating (1–5) and optional message.
    One review per user per course; users can update their review.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='course_reviews',
        help_text='User who left the review',
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text='Course this review is for',
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
        db_table = 'CourseReview'
        verbose_name = 'Course Review'
        verbose_name_plural = 'Course Reviews'
        unique_together = ['user', 'course']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['course'], name='coursereview_course_idx'),
            models.Index(fields=['user', 'course'], name='coursereview_user_course_idx'),
        ]

    def __str__(self):
        return f"{self.user.email} – {self.course.title} ({self.rating} stars)"


class CourseBundle(models.Model):
    """Named grouping of courses within a community; access is gated by assigned groups."""

    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name='course_bundles',
        help_text='Community this bundle belongs to',
    )
    title = models.CharField(max_length=255, help_text='Display title of the bundle')
    description = models.TextField(blank=True, null=True, help_text='Optional description')
    banner_url = models.URLField(
        blank=True,
        null=True,
        help_text='Optional bundle-only banner URL (not derived from courses)',
    )
    community_groups = models.ManyToManyField(
        CommunityGroup,
        related_name='course_bundles',
        blank=True,
        help_text='Community groups (tiers) that have access to this classroom',
    )
    is_published = models.BooleanField(
        default=False,
        help_text='If True, the classroom is visible/published to members',
    )
    published_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Set once when the classroom is first published; remains set if is_published is toggled off so downstream notifications fire only once.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'CourseBundle'
        verbose_name = 'Course Bundle'
        verbose_name_plural = 'Course Bundles'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['community']),
            models.Index(fields=['community', 'is_published'], name='CourseBundl_communi_pub_idx'),
        ]

    def save(self, *args, **kwargs):
        update_fields = kwargs.get('update_fields')
        if self.is_published and self.published_at is None:
            self.published_at = timezone.now()
            if update_fields is not None:
                kwargs['update_fields'] = list({*update_fields, 'published_at'})
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.community_id})"


class CourseBundleItem(models.Model):
    """Ordered membership of a course in a bundle."""

    bundle = models.ForeignKey(
        CourseBundle,
        on_delete=models.CASCADE,
        related_name='items',
        help_text='Bundle this row belongs to',
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='bundle_items',
        help_text='Course placed in the bundle',
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text='Sort order within the bundle (lower first)',
    )

    class Meta:
        db_table = 'CourseBundleItem'
        verbose_name = 'Course Bundle Item'
        verbose_name_plural = 'Course Bundle Items'
        ordering = ['order', 'id']
        constraints = [
            models.UniqueConstraint(
                fields=['bundle', 'course'],
                name='uniq_coursebundleitem_bundle_course',
            ),
        ]
        indexes = [
            models.Index(fields=['bundle', 'order'], name='cbi_bundle_order_idx'),
        ]

    def __str__(self):
        return f"{self.bundle_id}: {self.course_id} @ {self.order}"
