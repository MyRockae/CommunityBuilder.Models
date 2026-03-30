from django.db import models

from app_models.account.models import User
from app_models.community.models import Community


class StorageUsage(models.Model):
    """Track storage usage per file for subscription limit enforcement"""
    FILE_TYPE_CHOICES = [
        ('avatar', 'Avatar'),
        ('banner', 'Banner'),
        ('classroom_content', 'Classroom Content'),
        ('classroom_attachment', 'Classroom Attachment'),
        ('forum_attachment', 'Forum Attachment'),
        ('post_attachment', 'Post Attachment'),
        ('quiz_file', 'Quiz File'),
        ('blog_image', 'Blog Image'),
        ('featured_content', 'Featured Content'),
        ('other', 'Other'),
    ]

    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name='storage_usage',
        null=True,
        blank=True,
        help_text='Community this file belongs to (null for user profile files)',
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='storage_usage',
        help_text='Community owner (for per-owner storage limits)',
    )
    file_path = models.CharField(max_length=500, help_text='MinIO object path')
    file_size = models.BigIntegerField(help_text='File size in bytes')
    file_type = models.CharField(max_length=50, choices=FILE_TYPE_CHOICES, default='other')
    parent_entity_type = models.CharField(max_length=100, null=True, blank=True, help_text='Type of parent entity (e.g. Classroom, Post)')
    parent_entity_id = models.PositiveBigIntegerField(null=True, blank=True, help_text='ID of the parent entity')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'StorageUsage'
        verbose_name = 'Storage Usage'
        verbose_name_plural = 'Storage Usage'
        indexes = [
            models.Index(fields=['owner']),
            models.Index(fields=['community', 'owner']),
            models.Index(fields=['file_path']),
        ]

    def __str__(self):
        return f"{self.owner.email} - {self.file_path} - {self.file_size} bytes"
