from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from app_models.account.models import User
from app_models.community.models import Community


class CommunityBlogPost(models.Model):
    """
    Blog post for a community. Similar to BlogPost but belongs to a community.
    Slug is unique per community.
    """
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name='blog_posts',
        help_text='Community this blog post belongs to',
    )
    title = models.CharField(max_length=255, help_text='Title of the blog post')
    slug = models.SlugField(
        max_length=255,
        db_index=True,
        help_text='URL-friendly identifier (auto-generated from title, unique per community)',
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text='Short description/summary of the blog post',
    )
    blog_message = models.TextField(help_text='Content of the blog post')
    image_url = models.URLField(
        blank=True,
        null=True,
        help_text='URL of the blog post image',
    )
    writer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='community_blog_posts',
        help_text='User who wrote this blog post',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'CommunityBlogPost'
        verbose_name = 'Community Blog Post'
        verbose_name_plural = 'Community Blog Posts'
        ordering = ['-created_at']
        unique_together = [['community', 'slug']]

    def __str__(self):
        return f"{self.title} - {self.community.name}"

    def save(self, *args, **kwargs):
        if self.slug == '':
            self.slug = None

        if not self.slug:
            base_slug = slugify(self.title)
            if not base_slug:
                base_slug = "community-blog-post"

            timestamp = timezone.now().strftime('%Y%m%d%H%M%S%f')
            slug = f"{base_slug}-{timestamp}"

            original_slug = slug
            counter = 1
            while CommunityBlogPost.objects.filter(
                community=self.community, slug=slug
            ).exclude(pk=self.pk).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)


class CommunityBlogPostReply(models.Model):
    """
    Reply to a community blog post. Any user can reply; membership in the
    community is not required.
    """
    community_blog_post = models.ForeignKey(
        CommunityBlogPost,
        on_delete=models.CASCADE,
        related_name='replies',
        help_text='Blog post this reply belongs to',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='community_blog_post_replies',
        help_text='User who wrote this reply (no community membership required)',
    )
    message = models.TextField(help_text='Reply message content')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'CommunityBlogPostReply'
        verbose_name = 'Community Blog Post Reply'
        verbose_name_plural = 'Community Blog Post Replies'
        ordering = ['created_at']

    def __str__(self):
        return f"Reply by {self.user.email} on {self.community_blog_post.title}"
