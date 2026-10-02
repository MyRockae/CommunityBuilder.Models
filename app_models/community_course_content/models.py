from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from app_models.community.models import Community
from app_models.community_course.models import Course
from app_models.account.models import User


class LessonDefinition(models.Model):
    """Community-scoped canonical lesson (video, notes, materials). Not tied to a single course."""

    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name='lesson_definitions',
        help_text='Community this lesson definition belongs to',
    )
    title = models.CharField(max_length=255, help_text='Title of the lesson')
    description = models.TextField(blank=True, null=True, help_text='Description')
    notes = models.TextField(blank=True, null=True, help_text='Lesson notes/details')
    content_url = models.URLField(
        blank=True,
        null=True,
        help_text='Storage ref or external URL for non-video files; embeds use a full https URL',
    )
    thumbnail_url = models.URLField(blank=True, null=True, help_text='Thumbnail image URL (public)')
    content_source = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text='Source: application, youtube, vimeo, etc.',
    )
    VIDEO_STATUS_NONE = 'none'
    VIDEO_STATUS_PROCESSING = 'processing'
    VIDEO_STATUS_READY = 'ready'
    VIDEO_STATUS_FAILED = 'failed'
    VIDEO_STATUS_CHOICES = [
        (VIDEO_STATUS_NONE, 'None'),
        (VIDEO_STATUS_PROCESSING, 'Processing'),
        (VIDEO_STATUS_READY, 'Ready'),
        (VIDEO_STATUS_FAILED, 'Failed'),
    ]
    video_status = models.CharField(
        max_length=20,
        choices=VIDEO_STATUS_CHOICES,
        default=VIDEO_STATUS_NONE,
        help_text='Bunny Stream encode state',
    )
    bunny_video_id = models.CharField(
        max_length=36,
        blank=True,
        null=True,
        help_text='Bunny Stream video GUID',
    )
    bunny_thumbnail_file_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Bunny CDN thumbnail filename (e.g. thumbnail.jpg)',
    )
    video_error = models.TextField(
        blank=True,
        null=True,
        help_text='Last Bunny encode error when video_status is failed',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'LessonDefinition'
        verbose_name = 'Lesson Definition'
        verbose_name_plural = 'Lesson Definitions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.community_id})"


class CourseLessonPlacement(models.Model):
    """Links a lesson definition into a course syllabus with ordering."""

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lesson_placements',
        help_text='Course syllabus',
    )
    lesson_definition = models.ForeignKey(
        LessonDefinition,
        on_delete=models.CASCADE,
        related_name='placements',
        help_text='Canonical lesson row',
    )
    order = models.IntegerField(default=0, help_text='Order within this course (lower first)')
    is_preview = models.BooleanField(
        default=False,
        help_text='When true, unauthenticated visitors can view this syllabus row (notes and playback) on the public course page.',
    )

    class Meta:
        db_table = 'CourseLessonPlacement'
        verbose_name = 'Course Lesson Placement'
        verbose_name_plural = 'Course Lesson Placements'
        ordering = ['order', '-id']
        constraints = [
            models.UniqueConstraint(
                fields=['course', 'lesson_definition'],
                name='uniq_course_lessondefinition_placement',
            ),
        ]
        indexes = [
            models.Index(fields=['course'], name='clp_course_idx'),
            models.Index(fields=['lesson_definition'], name='clp_lesson_definition_idx'),
            models.Index(fields=['course', 'is_preview'], name='clp_course_preview_idx'),
        ]

    def __str__(self):
        return f"placement {self.pk} — {self.lesson_definition_id} in course {self.course_id}"


class LessonDefinitionAttachment(models.Model):
    """Supplementary files and lesson materials for a lesson definition (merged former attachment + resource)."""

    MATERIAL_KIND_LINK = 'link'
    MATERIAL_KIND_FILE = 'file'
    MATERIAL_KIND_VIDEO = 'video'
    MATERIAL_KIND_SUPPLEMENT = 'supplement'

    KIND_CHOICES = [
        (MATERIAL_KIND_LINK, 'Link'),
        (MATERIAL_KIND_FILE, 'File'),
        (MATERIAL_KIND_VIDEO, 'Video'),
        (MATERIAL_KIND_SUPPLEMENT, 'Supplement'),
    ]

    lesson_definition = models.ForeignKey(
        LessonDefinition,
        on_delete=models.CASCADE,
        related_name='attachments',
        help_text='Lesson this row belongs to',
    )
    title = models.CharField(max_length=255, help_text='Display title or label')
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, help_text='link, file (stored path), video (URL), supplement (legacy attachment)')
    url = models.TextField(blank=True, null=True, help_text='External URL or storage ref')
    content_source = models.CharField(max_length=50, blank=True, null=True, help_text='For video: youtube, vimeo, etc.')
    supplement_file_type = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text='When kind=supplement: image, video, pdf, file',
    )
    description = models.TextField(blank=True, null=True, help_text='Optional description (legacy attachments)')
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'LessonDefinitionAttachment'
        verbose_name = 'Lesson Definition Attachment'
        verbose_name_plural = 'Lesson Definition Attachments'
        ordering = ['order', 'id']
        indexes = [models.Index(fields=['lesson_definition'])]

    def __str__(self):
        return f"{self.title} ({self.kind})"


class LessonPlacementCompletion(models.Model):
    """Completion is per placement (per course syllabus), not per definition alone."""

    placement = models.ForeignKey(
        CourseLessonPlacement,
        on_delete=models.CASCADE,
        related_name='completions',
        help_text='Syllabus row completed',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='lesson_placement_completions',
        help_text='User who completed',
    )
    completed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'LessonPlacementCompletion'
        verbose_name = 'Lesson Placement Completion'
        verbose_name_plural = 'Lesson Placement Completions'
        unique_together = [['placement', 'user']]
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.user_id} completed placement {self.placement_id}"


class CourseCertificate(models.Model):
    """Stores certificates issued to users for completing all content in a course"""

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certificates', help_text='Course this certificate is for')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_certificates', help_text='User who received the certificate')
    certificate_url = models.URLField(blank=True, null=True, help_text='URL of the certificate file (if stored)')
    issued_at = models.DateTimeField(auto_now_add=True, help_text='When the certificate was issued')

    class Meta:
        db_table = 'CourseCertificate'
        verbose_name = 'Course Certificate'
        verbose_name_plural = 'Course Certificates'
        unique_together = ['course', 'user']
        ordering = ['-issued_at']

    def __str__(self):
        return f"Certificate for {self.user.email} - {self.course.name}"


class CompanionIndexOutbox(models.Model):
    """Durable Companion index job. Written in the same transaction as the lesson change."""

    EVENT_UPSERT = 'upsert'
    EVENT_DELETE = 'delete'
    EVENT_CHOICES = [(EVENT_UPSERT, 'upsert'), (EVENT_DELETE, 'delete')]

    STATUS_PENDING = 'pending'
    STATUS_COMPLETE = 'complete'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'pending'),
        (STATUS_COMPLETE, 'complete'),
        (STATUS_FAILED, 'failed'),
    ]

    event = models.CharField(max_length=16, choices=EVENT_CHOICES)
    community_id = models.BigIntegerField()
    lesson_definition_id = models.BigIntegerField()
    content_version = models.CharField(max_length=64, blank=True, default='')
    status = models.CharField(
        max_length=16,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        db_index=True,
    )
    last_error = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'CompanionIndexOutbox'
        ordering = ['id']
        indexes = [
            models.Index(fields=['status', 'created_at'], name='companion_outbox_status_idx'),
            models.Index(fields=['lesson_definition_id', 'status'], name='companion_outbox_lesson_idx'),
        ]

    def __str__(self):
        return f'{self.event} lesson={self.lesson_definition_id} ({self.status})'
