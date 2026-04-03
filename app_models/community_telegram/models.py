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
    platform_chat_id = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        help_text='Chat/channel id when using the platform bot (TELEGRAM_BOT_TOKEN); set by platform link or PATCH.',
    )
    private_bot_chat_id = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        help_text='Chat/channel id when using this community’s private BotFather token.',
    )
    platform_is_enabled = models.BooleanField(
        default=False,
        help_text='When true, platform bot sends are allowed for this community.',
    )
    private_is_enabled = models.BooleanField(
        default=False,
        help_text='When true, private bot sends are allowed for this community.',
    )
    platform_link_code = models.CharField(
        max_length=40,
        blank=True,
        null=True,
        db_index=True,
        help_text='Short-lived code; owner posts /link <code> in the group with the platform bot.',
    )
    platform_link_code_expires = models.DateTimeField(
        blank=True,
        null=True,
        help_text='When platform_link_code stops being valid.',
    )
    private_link_code = models.CharField(
        max_length=40,
        blank=True,
        null=True,
        db_index=True,
        help_text='Short-lived code for linking with the community private bot; owner posts /link <code>.',
    )
    private_link_code_expires = models.DateTimeField(
        blank=True,
        null=True,
        help_text='When private_link_code stops being valid.',
    )
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
