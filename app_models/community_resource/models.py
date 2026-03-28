from django.db import models
from app_models.community.models import Community, CommunityGroup
from app_models.shared.validators import slug_username_validator


class Resource(models.Model):
    """
    Resource is a folder for a community: name, friendly name, description.
    Can be associated with zero or many payment plans for access control.
    """
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name='resources',
        help_text='Community this resource belongs to',
    )
    name = models.CharField(
        max_length=255,
        validators=[slug_username_validator],
        help_text='Slug-like name (letters, numbers, hyphens, underscores). Used for URL/folder identifier.',
    )
    friendly_name = models.CharField(
        max_length=255,
        help_text='Display name for the resource (folder name shown on frontend)',
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text='Description of the resource',
    )
    payment_plans = models.ManyToManyField(
        CommunityGroup,
        related_name='resources',
        blank=True,
        help_text='Community groups (tiers) that have access to this resource. Zero or many.',
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this resource is active and visible. Inactive resources can be hidden from members.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Resource'
        verbose_name = 'Resource'
        verbose_name_plural = 'Resources'
        unique_together = ['community', 'name']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.friendly_name} - {self.community.name}"


class ResourceContent(models.Model):
    """
    A file within a resource. Files are stored in storage buckets; file_url points to the object.
    """
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name='contents',
        help_text='Resource (folder) this file belongs to',
    )
    title = models.CharField(max_length=255, help_text='Title of this content (file)')
    description = models.TextField(
        blank=True,
        null=True,
        help_text='Description of this content',
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text='Display order (lower numbers appear first)',
    )
    resource_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text='Type/category of resource content (API-defined string)',
    )
    content_type = models.CharField(
        max_length=50,
        help_text='Type of file (e.g. video, document, pdf, image). API-defined.',
    )
    content_source = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text='Source of the content, e.g. upload, youtube, vimeo (API-defined string)',
    )
    file_url = models.URLField(
        help_text='URL of the file in storage (e.g. MinIO bucket)',
    )
    thumbnail_url = models.URLField(
        blank=True,
        null=True,
        help_text='URL of the thumbnail image for this content',
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this content is active and visible. Inactive content can be hidden from members.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ResourceContent'
        verbose_name = 'Resource Content'
        verbose_name_plural = 'Resource Contents'
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.title} - {self.resource.friendly_name}"
