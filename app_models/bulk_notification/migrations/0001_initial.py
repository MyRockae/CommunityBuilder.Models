# Generated manually for bulk notification outbox, delivery log, preferences and suppression.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0004_user_token_version'),
        ('community', '0030_community_bunny_collection_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailSuppression',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('reason', models.CharField(choices=[('hard_bounce', 'Hard bounce'), ('spam_complaint', 'Spam complaint'), ('invalid', 'Invalid address'), ('manual', 'Manually suppressed')], default='hard_bounce', max_length=32)),
                ('detail', models.TextField(blank=True, default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Email suppression',
                'verbose_name_plural': 'Email suppressions',
                'db_table': 'EmailSuppression',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='NotificationBatch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(choices=[('town_hall_post', 'Town hall post'), ('forum_post', 'Forum post'), ('blog_post', 'Blog post'), ('classroom_published', 'Classroom published'), ('inactive_user', 'Inactive user'), ('views_momentum', 'Community views momentum')], help_text='Which notification this batch represents', max_length=32)),
                ('dedupe_key', models.CharField(help_text='Stable key per logical notification (e.g. town_hall_post:8412); makes re-triggers no-ops', max_length=128, unique=True)),
                ('object_id', models.BigIntegerField(blank=True, help_text='Primary key of the triggering object (post, blog post, classroom); null for platform-wide scans', null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('dispatched', 'Dispatched'), ('sending', 'Sending'), ('complete', 'Complete'), ('failed', 'Failed')], db_index=True, default='pending', max_length=16)),
                ('recipient_count', models.IntegerField(default=0)),
                ('sent_count', models.IntegerField(default=0)),
                ('failed_count', models.IntegerField(default=0)),
                ('last_error', models.TextField(blank=True, default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('actor', models.ForeignKey(blank=True, help_text='User who triggered the notification; excluded from recipients', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='triggered_notification_batches', to='account.user')),
                ('community', models.ForeignKey(blank=True, help_text='Null for platform-wide notifications such as inactive_user', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notification_batches', to='community.community')),
            ],
            options={
                'verbose_name': 'Notification batch',
                'verbose_name_plural': 'Notification batches',
                'db_table': 'NotificationBatch',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='MemberNotificationPreference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('muted_events', models.JSONField(blank=True, default=list, help_text='Event ids this member has opted out of (e.g. ["town_hall_post"])')),
                ('unsubscribed_all', models.BooleanField(default=False, help_text='When true, no bulk notifications are sent for this community')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('community', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='member_notification_preferences', to='community.community')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notification_preferences', to='account.user')),
            ],
            options={
                'verbose_name': 'Member notification preference',
                'verbose_name_plural': 'Member notification preferences',
                'db_table': 'MemberNotificationPreference',
            },
        ),
        migrations.CreateModel(
            name='NotificationDelivery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('event_type', models.CharField(choices=[('town_hall_post', 'Town hall post'), ('forum_post', 'Forum post'), ('blog_post', 'Blog post'), ('classroom_published', 'Classroom published'), ('inactive_user', 'Inactive user'), ('views_momentum', 'Community views momentum')], help_text='Denormalised from the batch so cooldown lookups avoid a join', max_length=32)),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('error', models.TextField(blank=True, default='')),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deliveries', to='bulk_notification.notificationbatch')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notification_deliveries', to='account.user')),
            ],
            options={
                'verbose_name': 'Notification delivery',
                'verbose_name_plural': 'Notification deliveries',
                'db_table': 'NotificationDelivery',
            },
        ),
        migrations.AddIndex(
            model_name='notificationbatch',
            index=models.Index(fields=['status', 'created_at'], name='notif_batch_status_idx'),
        ),
        migrations.AddIndex(
            model_name='notificationbatch',
            index=models.Index(fields=['event_type', 'created_at'], name='notif_batch_event_idx'),
        ),
        migrations.AddConstraint(
            model_name='membernotificationpreference',
            constraint=models.UniqueConstraint(fields=('user', 'community'), name='member_notif_pref_uq'),
        ),
        migrations.AddIndex(
            model_name='notificationdelivery',
            index=models.Index(fields=['user', 'event_type', '-sent_at'], name='notif_deliv_cooldown_idx'),
        ),
        migrations.AddConstraint(
            model_name='notificationdelivery',
            constraint=models.UniqueConstraint(fields=('batch', 'user'), name='notif_delivery_batch_user_uq'),
        ),
    ]
