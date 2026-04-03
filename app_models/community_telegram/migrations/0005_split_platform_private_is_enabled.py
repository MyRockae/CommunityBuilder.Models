from django.db import migrations, models


def copy_is_enabled_to_both(apps, schema_editor):
    CommunityTelegram = apps.get_model('community_telegram', 'CommunityTelegram')
    for row in CommunityTelegram.objects.all():
        v = bool(getattr(row, 'is_enabled', False))
        row.platform_is_enabled = v
        row.private_is_enabled = v
        row.save(update_fields=['platform_is_enabled', 'private_is_enabled'])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('community_telegram', '0004_communitytelegram_private_link_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='communitytelegram',
            name='platform_is_enabled',
            field=models.BooleanField(
                default=False,
                help_text='When true, platform bot sends are allowed for this community.',
            ),
        ),
        migrations.AddField(
            model_name='communitytelegram',
            name='private_is_enabled',
            field=models.BooleanField(
                default=False,
                help_text='When true, private bot sends are allowed for this community.',
            ),
        ),
        migrations.RunPython(copy_is_enabled_to_both, noop),
        migrations.RemoveField(
            model_name='communitytelegram',
            name='is_enabled',
        ),
    ]
