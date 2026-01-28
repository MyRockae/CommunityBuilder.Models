from django.db import models
from app_models.community.models import Community, PaymentPlan
from app_models.account.models import User


class Meeting(models.Model):
    """Meeting model for community meetings"""
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='meetings')
    title = models.CharField(max_length=255, help_text='Meeting title')
    description = models.TextField(blank=True, null=True, help_text='Meeting description/notes')
    start_datetime = models.DateTimeField(help_text='Start date and time')
    end_datetime = models.DateTimeField(help_text='End date and time')
    location = models.CharField(max_length=500, blank=True, null=True, help_text='Physical meeting location')
    meeting_url = models.URLField(blank=True, null=True, help_text='Virtual meeting URL (Zoom, Google Meet, etc.)')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_meetings')
    payment_plans = models.ManyToManyField(PaymentPlan, related_name='meetings', blank=True, help_text='Payment plans that have access to this meeting')
    attendees = models.ManyToManyField(User, related_name='meetings_attending', blank=True, help_text='Users invited to the meeting')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'Meeting'
        verbose_name = 'Meeting'
        verbose_name_plural = 'Meetings'
        ordering = ['start_datetime']
    
    def __str__(self):
        return f"{self.title} - {self.community.name}"
