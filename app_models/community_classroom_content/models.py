from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from app_models.community.models import Community
from app_models.community_classroom.models import Classroom
from app_models.account.models import User


class LessonDefinition(models.Model):
    """Community-scoped canonical lesson (video, notes, materials). Not tied to a single classroom."""

    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name='lesson_definitions',
        help_text='Community this lesson definition belongs to',
    )
    title = models.CharField(max_length=255, help_text='Title of the lesson')
    description = models.TextField(blank=True, null=True, help_text='Description')
    notes = models.TextField(blank=True, null=True, help_text='Lesson notes/details')
    content_url = models.URLField(blank=True, null=True, help_text='URL of main content (video) or MinIO object path')
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
        help_text='Adaptive HLS transcode state (video bucket); none for non-video or tier without feature',
    )
    hls_manifest_object = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text='MinIO object key for master.m3u8 in the video transcode bucket',
    )
    video_error = models.TextField(
        blank=True,
        null=True,
        help_text='Last transcode error message when video_status is failed',
    )
    video_job_id = models.CharField(
        max_length=36,
        blank=True,
        null=True,
        help_text='VideoService transcode job UUID',
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


class ClassroomLessonPlacement(models.Model):
    """Links a lesson definition into a classroom syllabus with ordering."""

    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name='lesson_placements',
        help_text='Classroom syllabus',
    )
    lesson_definition = models.ForeignKey(
        LessonDefinition,
        on_delete=models.CASCADE,
        related_name='placements',
        help_text='Canonical lesson row',
    )
    order = models.IntegerField(default=0, help_text='Order within this classroom (lower first)')

    class Meta:
        db_table = 'ClassroomLessonPlacement'
        verbose_name = 'Classroom Lesson Placement'
        verbose_name_plural = 'Classroom Lesson Placements'
        ordering = ['order', '-id']
        constraints = [
            models.UniqueConstraint(
                fields=['classroom', 'lesson_definition'],
                name='uniq_classroom_lessondefinition_placement',
            ),
        ]
        indexes = [
            models.Index(fields=['classroom']),
            models.Index(fields=['lesson_definition']),
        ]

    def __str__(self):
        return f"placement {self.pk} — {self.lesson_definition_id} in classroom {self.classroom_id}"


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
    url = models.TextField(blank=True, null=True, help_text='External URL or MinIO object path')
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
    """Completion is per placement (per classroom syllabus), not per definition alone."""

    placement = models.ForeignKey(
        ClassroomLessonPlacement,
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


class ClassroomCertificate(models.Model):
    """Stores certificates issued to users for completing all content in a classroom"""

    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='certificates', help_text='Classroom this certificate is for')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='classroom_certificates', help_text='User who received the certificate')
    certificate_url = models.URLField(blank=True, null=True, help_text='URL of the certificate file (if stored)')
    issued_at = models.DateTimeField(auto_now_add=True, help_text='When the certificate was issued')

    class Meta:
        db_table = 'ClassroomCertificate'
        verbose_name = 'Classroom Certificate'
        verbose_name_plural = 'Classroom Certificates'
        unique_together = ['classroom', 'user']
        ordering = ['-issued_at']

    def __str__(self):
        return f"Certificate for {self.user.email} - {self.classroom.name}"
