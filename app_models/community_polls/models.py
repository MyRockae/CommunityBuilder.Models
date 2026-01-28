from django.db import models
from app_models.community.models import Community, PaymentPlan
from app_models.account.models import User


class Poll(models.Model):
    """Poll model for community - associated with payment plans for access control"""
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='polls', help_text='Community this poll belongs to')
    title = models.CharField(max_length=255, help_text='Title/question of the poll')
    description = models.TextField(blank=True, null=True, help_text='Description or additional context for the poll')
    payment_plans = models.ManyToManyField(PaymentPlan, related_name='polls', blank=True, help_text='Payment plans that have access to this poll. Owners, co-owners, and moderators have access regardless of payment plan.')
    is_active = models.BooleanField(default=True, help_text='Whether this poll is currently active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'Poll'
        verbose_name = 'Poll'
        verbose_name_plural = 'Polls'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.community.name}"


class PollOption(models.Model):
    """Poll option/choice model - represents a choice in a poll"""
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='options', help_text='Poll this option belongs to')
    text = models.CharField(max_length=255, help_text='Text of the poll option')
    order = models.IntegerField(default=0, help_text='Order/position of this option in the poll')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'PollOption'
        verbose_name = 'Poll Option'
        verbose_name_plural = 'Poll Options'
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.text} - {self.poll.title}"


class PollVote(models.Model):
    """Poll vote model - tracks user votes on poll options"""
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='votes', help_text='Poll this vote belongs to')
    option = models.ForeignKey(PollOption, on_delete=models.CASCADE, related_name='votes', help_text='Poll option that was voted for')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='poll_votes', help_text='User who cast the vote')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'PollVote'
        verbose_name = 'Poll Vote'
        verbose_name_plural = 'Poll Votes'
        unique_together = ['poll', 'user']  # Each user can only vote once per poll
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.option.text} - {self.poll.title}"
