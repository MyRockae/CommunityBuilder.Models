from django.db import models
from app_models.account.models import User
from app_models.community.models import Community


class PublicFeed(models.Model):
    """
    Public feed item posted by a community.
    Only communities can post to public feeds; posted_by is the community member who created it.
    """
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name='public_feeds',
        help_text='Community that owns this feed item',
    )
    posted_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='public_feed_posts',
        help_text='Community member who posted this on behalf of the community',
    )
    parent_feed = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        help_text='Parent feed if this is a reply',
    )
    message = models.TextField(help_text='Feed message content')
    allow_replies = models.BooleanField(
        default=True,
        help_text='If true, users can reply to this feed. If false, replies are disabled.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'PublicFeeds'
        verbose_name = 'Public Feed'
        verbose_name_plural = 'Public Feeds'
        ordering = ['-created_at']

    def __str__(self):
        return f"Feed by {self.community.name} (posted by {self.posted_by.email})"


class PublicFeedsAttachment(models.Model):
    """Attachment model for public feed images/videos."""
    ATTACHMENT_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]

    public_feed = models.ForeignKey(
        PublicFeed,
        on_delete=models.CASCADE,
        related_name='attachments',
    )
    file_url = models.URLField(help_text='URL of the attached file')
    file_type = models.CharField(
        max_length=10,
        choices=ATTACHMENT_TYPE_CHOICES,
        help_text='Type of attachment (image or video)',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'PublicFeedsAttachment'
        verbose_name = 'Public Feeds Attachment'
        verbose_name_plural = 'Public Feeds Attachments'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.file_type} attachment for public feed {self.public_feed.id}"


class PublicFeedsLike(models.Model):
    """Model to track user likes on public feeds."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='public_feed_likes',
    )
    public_feed = models.ForeignKey(
        PublicFeed,
        on_delete=models.CASCADE,
        related_name='likes',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'PublicFeedsLike'
        verbose_name = 'Public Feeds Like'
        verbose_name_plural = 'Public Feeds Likes'
        unique_together = ['user', 'public_feed']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} liked public feed {self.public_feed.id}"
