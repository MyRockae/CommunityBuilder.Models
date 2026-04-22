import django.db.models.deletion
from django.db import migrations, models


def forwards_create_settings_rows(apps, schema_editor):
    Community = apps.get_model('community', 'Community')
    CommunitySettings = apps.get_model('community', 'CommunitySettings')
    for community in Community.objects.all().iterator():
        CommunitySettings.objects.get_or_create(community_id=community.pk)


def backwards_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0019_communitygroup_avatar_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommunitySettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'owner_notification_preferences',
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text=(
                            'Owner/co-owner notification opt-ins by event type. Keys are stable event ids '
                            '(e.g. feedback, public_feed_reply, blog_reply, quiz_submission); values are typically '
                            'boolean. Omitted keys are treated as off (opt-in).'
                        ),
                    ),
                ),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                (
                    'community',
                    models.OneToOneField(
                        help_text='Community these settings belong to',
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='settings',
                        to='community.community',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Community settings',
                'verbose_name_plural': 'Community settings',
                'db_table': 'CommunitySettings',
            },
        ),
        migrations.RunPython(forwards_create_settings_rows, backwards_noop),
    ]
