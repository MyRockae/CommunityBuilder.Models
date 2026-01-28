from django.db import models
from app_models.community_classroom.models import Classroom
from app_models.account.models import User


class ClassroomContent(models.Model):
    """Classroom content model - contains title, description, notes, content_url, and content_type"""
    CONTENT_TYPE_CHOICES = [
        ('video', 'Video'),
        ('document', 'Document'),
        ('article', 'Article'),
        ('link', 'Link'),
        ('other', 'Other'),
    ]
    
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='contents', help_text='Classroom this content belongs to')
    title = models.CharField(max_length=255, help_text='Title of the classroom content')
    description = models.TextField(blank=True, null=True, help_text='Description of the classroom content')
    notes = models.TextField(blank=True, null=True, help_text='Classroom content notes/details')
    content_url = models.URLField(blank=True, null=True, help_text='URL of the classroom content (video, document, etc.)')
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default='other', help_text='Type of content (video, document, article, link, other)')
    is_active = models.BooleanField(default=True, help_text='Whether this content is active and visible to members. Owners and moderators can see inactive content.')
    order = models.IntegerField(default=0, help_text='Display order (lower numbers appear first). Used for drag-and-drop reordering by owners/moderators.')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ClassroomContent'
        verbose_name = 'Classroom Content'
        verbose_name_plural = 'Classroom Contents'
        ordering = ['order', '-created_at']
    
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
