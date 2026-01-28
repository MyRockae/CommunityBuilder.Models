from django.db import models
from app_models.account.models import User
from app_models.community.models import Community, PaymentPlan
from app_models.shared.validators import slug_username_validator

class Classroom(models.Model):
    """Classroom model for community - contains name, title, description, and banner"""
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='classrooms')
    name = models.CharField(
        max_length=255,
        validators=[slug_username_validator],
        help_text='Name of the classroom. Only letters, numbers, hyphens (-) and underscores (_) allowed.',
    )
    title = models.CharField(max_length=255, help_text='Title of the classroom')
    description = models.TextField(blank=True, null=True, help_text='Description of the classroom')
    banner_url = models.URLField(blank=True, null=True, help_text='URL of the classroom banner image')
    payment_plans = models.ManyToManyField(PaymentPlan, related_name='classrooms', blank=True, help_text='Payment plans that have access to this classroom')
    enforce_progression = models.BooleanField(default=False, help_text='If True, users must complete content in order (one at a time). Owners/moderators can view all content regardless.')
    issue_certificate = models.BooleanField(default=False, help_text='If True, users will receive a certificate when all content in the classroom is completed')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'Classroom'
        verbose_name = 'Classroom'
        verbose_name_plural = 'Classrooms'
        unique_together = ['community', 'name']  # Each community can have unique classroom names
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.community.name}"
