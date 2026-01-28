from django.db import models
from app_models.account.models import User
from app_models.community.models import Community


class Conversation(models.Model):
    """Conversation model - represents a chat between 2 or more members within a community"""
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='conversations', help_text='Community this conversation belongs to')
    participants = models.ManyToManyField(User, through='ConversationParticipant', related_name='conversations', help_text='Users participating in this conversation')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_message_at = models.DateTimeField(null=True, blank=True, help_text='Timestamp of the last message in this conversation')
    
    class Meta:
        db_table = 'Conversation'
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'
        ordering = ['-last_message_at', '-created_at']
    
    def __str__(self):
        return f"Conversation in {self.community.name} ({self.participants.count()} participants)"


class ConversationParticipant(models.Model):
    """Through model for Conversation participants - tracks when user joined, last read, etc."""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='conversation_participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversation_participations')
    joined_at = models.DateTimeField(auto_now_add=True)
    last_read_at = models.DateTimeField(null=True, blank=True, help_text='When the user last read messages in this conversation')
    is_muted = models.BooleanField(default=False, help_text='Whether the user has muted this conversation')
    
    class Meta:
        db_table = 'ConversationParticipant'
        verbose_name = 'Conversation Participant'
        verbose_name_plural = 'Conversation Participants'
        unique_together = ['conversation', 'user']
    
    def __str__(self):
        return f"{self.user.email} in conversation {self.conversation.id}"


class Message(models.Model):
    """Message model - individual messages in a conversation"""
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('file', 'File'),
    ]
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages', help_text='Conversation this message belongs to')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', help_text='User who sent this message')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE_CHOICES, default='text', help_text='Type of message')
    content = models.TextField(help_text='Message content (text or file URL)')
    is_read = models.BooleanField(default=False, help_text='Whether the message has been read by recipients')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'Message'
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message from {self.sender.email} in conversation {self.conversation.id}"
