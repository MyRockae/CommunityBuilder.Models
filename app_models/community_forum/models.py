from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from app_models.account.models import User
from app_models.community.models import Community, PaymentPlan

class Forum(models.Model):
    """Forum model for community - each community can have multiple forums"""
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='forums')
    name = models.CharField(max_length=255, help_text='Name of the forum (e.g., "General", "Announcements")')
    description = models.TextField(blank=True, null=True, help_text='Description of the forum')
    restrict_posting_to_owners_moderators = models.BooleanField(default=False, help_text='If true, only owners and moderators can post on this forum. If false, all members can post.')
    payment_plans = models.ManyToManyField(PaymentPlan, related_name='forums', blank=True, help_text='Payment plans that have access to this forum')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'Forum'
        verbose_name = 'Forum'
        verbose_name_plural = 'Forums'
        ordering = ['created_at']
        unique_together = ['community', 'name']  # Each community can have unique forum names
    
    def __str__(self):
        return f"{self.name} - {self.community.name}"

class Post(models.Model):
    """Post model for community forum"""
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE, related_name='posts')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    parent_post = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', help_text='Parent post if this is a reply')
    message = models.TextField(help_text='Post message content')
    allow_replies = models.BooleanField(default=True, help_text='If true, users can reply to this post. If false, replies are disabled.')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'Post'
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Post by {self.user.email} on {self.forum.name}"

class PostAttachment(models.Model):
    """Attachment model for post images/videos"""
    ATTACHMENT_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='attachments')
    file_url = models.URLField(help_text='URL of the attached file')
    file_type = models.CharField(max_length=10, choices=ATTACHMENT_TYPE_CHOICES, help_text='Type of attachment (image or video)')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'PostAttachment'
        verbose_name = 'Post Attachment'
        verbose_name_plural = 'Post Attachments'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.file_type} attachment for post {self.post.id}"

class PostLike(models.Model):
    """Model to track user likes on posts (works for both forum posts and townhall posts)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'PostLike'
        verbose_name = 'Post Like'
        verbose_name_plural = 'Post Likes'
        unique_together = ['user', 'post']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} liked post {self.post.id}"

# Signal to automatically create a "town_hall" forum when a community is created
@receiver(post_save, sender=Community)
def create_town_hall_forum(sender, instance, created, **kwargs):
    """Automatically create a 'town_hall' forum when a community is created"""
    if created:
        Forum.objects.get_or_create(
            community=instance,
            name='town_hall',
            defaults={
                'description': 'Town Hall discussion forum for the community',
                'restrict_posting_to_owners_moderators': False
            }
        )
