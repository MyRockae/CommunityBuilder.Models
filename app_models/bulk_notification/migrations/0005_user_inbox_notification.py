import django.db.models.deletion
from django.db import migrations, models


EVENT_CHOICES = [
    ('town_hall_post', 'Town hall post'),
    ('forum_post', 'Forum post'),
    ('blog_post', 'Blog post'),
    ('course_published', 'Course published'),
    ('resource_activated', 'Resource content activated'),
    ('classroom_created', 'Classroom created'),
    ('poll_created', 'Poll created'),
    ('meeting_created', 'Meeting created'),
    ('join_request', 'Join request'),
    ('community_feedback', 'Community feedback'),
    ('quiz_submission', 'Quiz submission'),
    ('blog_reply', 'Blog reply'),
    ('public_feed_reply', 'Public feed reply'),
    ('inactive_user', 'Inactive user'),
    ('views_momentum', 'Community views momentum'),
    ('marketing_campaign', 'Marketing campaign'),
]


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_user_token_version'),
        ('bulk_notification', '0004_rename_classroom_published'),
        ('community', '0030_community_bunny_collection_id'),
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
            name='UserInboxNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(choices=EVENT_CHOICES, max_length=32)),
                ('object_id', models.BigIntegerField()),
                ('object_type', models.CharField(blank=True, default='', max_length=32)),
                ('actor_name', models.CharField(blank=True, default='', max_length=255)),
                ('actor_avatar_ref', models.CharField(blank=True, default='', max_length=1024)),
                ('title', models.CharField(blank=True, default='', max_length=255)),
                ('excerpt', models.TextField(blank=True, default='')),
                ('deep_link', models.CharField(blank=True, default='', max_length=512)),
                ('read_at', models.DateTimeField(blank=True, null=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('actor', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='triggered_inbox_notifications',
                    to='account.user',
                )),
                ('batch', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='inbox_notifications',
                    to='bulk_notification.notificationbatch',
                )),
                ('community', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='inbox_notifications',
                    to='community.community',
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='inbox_notifications',
                    to='account.user',
                )),
            ],
            options={
                'verbose_name': 'User inbox notification',
                'verbose_name_plural': 'User inbox notifications',
                'db_table': 'UserInboxNotification',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='userinboxnotification',
            constraint=models.UniqueConstraint(
                fields=('user', 'community', 'event_type', 'object_id'),
                name='inbox_notif_user_event_obj_uq',
            ),
        ),
        migrations.AddIndex(
            model_name='userinboxnotification',
            index=models.Index(
                fields=['user', 'community', 'deleted_at', '-created_at'],
                name='inbox_notif_list_idx',
            ),
        ),
        migrations.AddIndex(
            model_name='userinboxnotification',
            index=models.Index(
                fields=['user', 'community', 'read_at'],
                name='inbox_notif_unread_idx',
            ),
        ),
    ]
