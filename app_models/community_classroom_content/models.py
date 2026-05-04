from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, F
from django.utils import timezone
from app_models.community_classroom.models import Classroom
from app_models.account.models import User


class ClassroomContent(models.Model):
    """Classroom content model - video only; content_source indicates upload vs youtube, vimeo, twitter, etc."""
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='contents', help_text='Classroom this content belongs to')
    title = models.CharField(max_length=255, help_text='Title of the classroom content')
    description = models.TextField(blank=True, null=True, help_text='Description of the classroom content')
    notes = models.TextField(blank=True, null=True, help_text='Classroom content notes/details')
    content_url = models.URLField(blank=True, null=True, help_text='URL of the classroom content (video)')
    thumbnail_url = models.URLField(blank=True, null=True, help_text='URL of the thumbnail image for this content')
    content_source = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text='Source of the video, e.g. upload, youtube, vimeo, twitter (API-defined string)',
    )
    is_active = models.BooleanField(default=True, help_text='Whether this content is active and visible to members. Owners and moderators can see inactive content.')
    activated_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Set once when the content is first activated; remains set if is_active is toggled off so downstream notifications fire only once.',
    )
    order = models.IntegerField(default=0, help_text='Display order (lower numbers appear first). Used for drag-and-drop reordering by owners/moderators.')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ClassroomContent'
        verbose_name = 'Classroom Content'
        verbose_name_plural = 'Classroom Contents'
        ordering = ['order', '-created_at']

    def save(self, *args, **kwargs):
        update_fields = kwargs.get('update_fields')
        if self.is_active and self.activated_at is None:
            self.activated_at = timezone.now()
            if update_fields is not None:
                kwargs['update_fields'] = list({*update_fields, 'activated_at'})
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.classroom.name}"


class ClassroomAttachment(models.Model):
    """Attachment model for classroom content files - similar to PostAttachment"""
    ATTACHMENT_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('pdf', 'PDF'),
        ('file', 'File'),
    ]
    
    content = models.ForeignKey(ClassroomContent, on_delete=models.CASCADE, related_name='attachments', help_text='Classroom content this attachment belongs to')
    file_url = models.URLField(help_text='URL of the attached file')
    file_type = models.CharField(max_length=10, choices=ATTACHMENT_TYPE_CHOICES, help_text='Type of attachment (image, video, pdf, or file)')
    description = models.TextField(blank=True, null=True, help_text='Description of the attachment')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ClassroomAttachment'
        verbose_name = 'Classroom Attachment'
        verbose_name_plural = 'Classroom Attachments'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.file_type} attachment for {self.content.title}"


class ClassroomResource(models.Model):
    """Named lesson materials for a content item: links, uploaded files, or external video URLs — distinct from community Resource library."""

    KIND_CHOICES = [
        ('link', 'Link'),
        ('file', 'File'),
        ('video', 'Video'),
    ]

    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name='classroom_resources',
        help_text='Classroom this resource belongs to (must match content.classroom)',
    )
    content = models.ForeignKey(
        ClassroomContent,
        on_delete=models.CASCADE,
        related_name='classroom_resources',
        help_text='Classroom content item this resource supplements',
    )
    title = models.CharField(max_length=255, help_text='Display label for the resource')
    kind = models.CharField(max_length=10, choices=KIND_CHOICES, help_text='link, file (stored object path), or video (external URL)')
    url = models.TextField(
        blank=True,
        null=True,
        help_text='External URL for link/video, or MinIO object path for uploaded files',
    )
    content_source = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text='For video kind: e.g. youtube, vimeo (optional)',
    )
    order = models.IntegerField(default=0, help_text='Display order within the content item')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ClassroomResource'
        verbose_name = 'Classroom Resource'
        verbose_name_plural = 'Classroom Resources'
        ordering = ['order', 'id']
        indexes = [
            models.Index(fields=['content']),
            models.Index(fields=['classroom']),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(content__classroom_id=F('classroom_id')),
                name='classroom_resource_content_classroom_match',
            ),
        ]

    def clean(self):
        super().clean()
        if self.content_id and self.classroom_id and self.content.classroom_id != self.classroom_id:
            raise ValidationError('classroom must match the classroom of content.')

    def __str__(self):
        return f"{self.title} ({self.kind}) — {self.content.title}"


class ClassroomContentCompletion(models.Model):
    """Tracks which content items a user has completed"""
    content = models.ForeignKey(ClassroomContent, on_delete=models.CASCADE, related_name='completions', help_text='Content that was completed')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='classroom_content_completions', help_text='User who completed the content')
    completed_at = models.DateTimeField(auto_now_add=True, help_text='When the content was marked as complete')
    
    class Meta:
        db_table = 'ClassroomContentCompletion'
        verbose_name = 'Classroom Content Completion'
        verbose_name_plural = 'Classroom Content Completions'
        unique_together = ['content', 'user']  # Each user can only complete each content once
        ordering = ['-completed_at']
    
    def __str__(self):
        return f"{self.user.email} completed {self.content.title}"


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
        unique_together = ['classroom', 'user']  # Each user can only have one certificate per classroom
        ordering = ['-issued_at']
    
    def __str__(self):
        return f"Certificate for {self.user.email} - {self.classroom.name}"
