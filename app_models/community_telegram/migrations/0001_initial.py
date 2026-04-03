# Generated manually for CommunityTelegram

import django.db.models.deletion
from django.db import migrations, models


def create_telegram_rows_for_existing_communities(apps, schema_editor):
    Community = apps.get_model('community', 'Community')
    CommunityTelegram = apps.get_model('community_telegram', 'CommunityTelegram')
    for community in Community.objects.all():
        CommunityTelegram.objects.get_or_create(community_id=community.pk)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('community', '0017_communitygroup_billing_period_flags'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommunityTelegram',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.TextField(blank=True, help_text='Optional BotFather token when using a private bot; empty uses platform bot only.', null=True)),
                ('chat_id', models.CharField(blank=True, help_text='Telegram chat id for the linked group or channel.', max_length=64, null=True)),
                ('is_enabled', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('community', models.OneToOneField(db_column='community_id', on_delete=django.db.models.deletion.CASCADE, related_name='telegram_settings', to='community.community')),
            ],
            options={
                'verbose_name': 'Community Telegram',
                'verbose_name_plural': 'Community Telegram',
                'db_table': 'CommunityTelegram',
            },
        ),
        migrations.RunPython(create_telegram_rows_for_existing_communities, noop_reverse),
    ]
