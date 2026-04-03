from django.db import migrations, models


def copy_chat_id_to_both(apps, schema_editor):
    CommunityTelegram = apps.get_model('community_telegram', 'CommunityTelegram')
    for row in CommunityTelegram.objects.exclude(chat_id__isnull=True).exclude(chat_id=''):
        cid = (row.chat_id or '').strip()
        if not cid:
            continue
        row.platform_chat_id = cid
        row.private_bot_chat_id = cid
        row.save(update_fields=['platform_chat_id', 'private_bot_chat_id'])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('community_telegram', '0002_communitytelegram_platform_link_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='communitytelegram',
            name='platform_chat_id',
            field=models.CharField(
                blank=True,
                help_text='Chat/channel id for sends using the platform bot (TELEGRAM_BOT_TOKEN).',
                max_length=64,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='communitytelegram',
            name='private_bot_chat_id',
            field=models.CharField(
                blank=True,
                help_text='Chat/channel id for sends using this community’s private bot token.',
                max_length=64,
                null=True,
            ),
        ),
        migrations.RunPython(copy_chat_id_to_both, noop),
        migrations.RemoveField(
            model_name='communitytelegram',
            name='chat_id',
        ),
    ]
