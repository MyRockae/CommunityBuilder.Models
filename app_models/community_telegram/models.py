from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from app_models.community.models import Community


class CommunityTelegram(models.Model):
    """Per-community Telegram bot settings (one row per community)."""

    community = models.OneToOneField(
        Community,
        on_delete=models.CASCADE,
        related_name='telegram_settings',
        db_column='community_id',
    )
    token = models.TextField(
        blank=True,
        null=True,
        help_text='Optional BotFather token when using a private bot; empty uses platform bot only.',
    )
    chat_id = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        help_text='Telegram chat id for the linked group or channel.',
    )
    is_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'CommunityTelegram'
        verbose_name = 'Community Telegram'
        verbose_name_plural = 'Community Telegram'

    def __str__(self):
        return f'Telegram settings for {self.community_id}'


@receiver(post_save, sender=Community)
def _create_community_telegram(sender, instance, created, **kwargs):
    if created:
        CommunityTelegram.objects.get_or_create(community=instance)
