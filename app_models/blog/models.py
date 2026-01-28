from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from app_models.account.models import User


class BlogPost(models.Model):
    """Blog post model for FAQs and stories"""
    title = models.CharField(max_length=255, help_text='Title of the blog post')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, help_text='URL-friendly identifier (auto-generated from title)')
    description = models.TextField(blank=True, null=True, help_text='Short description/summary of the blog post')
    blog_message = models.TextField(help_text='Content of the blog post')
    image_url = models.URLField(blank=True, null=True, help_text='URL of the blog post image')
    writer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='blog_posts', help_text='User who wrote this blog post')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Treat empty strings as None for slug
        if self.slug == '':
            self.slug = None
        
        # Generate slug from title if not provided
        if not self.slug:
            # Generate base slug from title
            base_slug = slugify(self.title)
            if not base_slug:  # If title doesn't generate a valid slug
                base_slug = "blog-post"
            
            # Generate timestamp with microseconds for uniqueness (YYYYMMDDHHMMSS format)
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S%f')  # Includes microseconds
            
            # Create slug with title and timestamp (no ID needed - timestamp ensures uniqueness)
            slug = f"{base_slug}-{timestamp}"
            
            # Ensure uniqueness (in case of collision, add counter)
            original_slug = slug
            counter = 1
            while BlogPost.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1
            
            self.slug = slug
        
        # Save normally (no double-save needed)
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'BlogPost'
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'
        ordering = ['-created_at']
