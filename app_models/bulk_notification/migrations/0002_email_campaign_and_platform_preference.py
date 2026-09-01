# Generated manually for admin-authored marketing campaigns and account-level opt-out.

import django.db.models.deletion
from django.db import migrations, models

EVENT_CHOICES = [
    ('town_hall_post', 'Town hall post'),
    ('forum_post', 'Forum post'),
    ('blog_post', 'Blog post'),
    ('classroom_published', 'Classroom published'),
    ('inactive_user', 'Inactive user'),
    ('views_momentum', 'Community views momentum'),
    ('marketing_campaign', 'Marketing campaign'),
]


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_user_token_version'),
        ('bulk_notification', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificationbatch',
            name='event_type',
            field=models.CharField(
                choices=EVENT_CHOICES,
                help_text='Which notification this batch represents',
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name='notificationdelivery',
            name='event_type',
            field=models.CharField(
                choices=EVENT_CHOICES,
                help_text='Denormalised from the batch so cooldown lookups avoid a join',
                max_length=32,
            ),
        ),
        migrations.CreateModel(
            name='PlatformNotificationPreference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('marketing_opt_out', models.BooleanField(default=False, help_text='When true, the user receives no marketing campaigns')),
                ('inactive_user_opt_out', models.BooleanField(default=False, help_text='When true, the user receives no re-engagement reminders')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='platform_notification_preference', to='account.user')),
            ],
            options={
                'verbose_name': 'Platform notification preference',
                'verbose_name_plural': 'Platform notification preferences',
                'db_table': 'PlatformNotificationPreference',
            },
        ),
        migrations.CreateModel(
            name='EmailCampaign',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Internal name, never shown to recipients', max_length=255)),
                ('subject', models.CharField(max_length=255)),
                ('preheader', models.CharField(blank=True, default='', help_text='Preview text shown after the subject in most inboxes', max_length=255)),
                ('content_json', models.JSONField(blank=True, default=dict, help_text='Editor document; rendered to email-safe HTML at send time')),
                ('hero_image_url', models.CharField(blank=True, default='', help_text='Storage ref for the banner image; must live under the public/ zone', max_length=1024)),
                ('audience', models.CharField(choices=[('all_users', 'All verified active users')], default='all_users', max_length=32)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('sending', 'Sending'), ('sent', 'Sent'), ('failed', 'Failed')], db_index=True, default='draft', max_length=16)),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('batch', models.ForeignKey(blank=True, help_text='Set when the campaign is sent; source of truth for delivery counts', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='email_campaigns', to='bulk_notification.notificationbatch')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='email_campaigns', to='account.user')),
            ],
            options={
                'verbose_name': 'Email campaign',
                'verbose_name_plural': 'Email campaigns',
                'db_table': 'EmailCampaign',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='emailcampaign',
            index=models.Index(fields=['status', 'created_at'], name='email_campaign_status_idx'),
        ),
    ]
