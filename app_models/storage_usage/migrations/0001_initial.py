# State-only: StorageUsage table already exists under app_subscription.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0001_initial'),
        ('app_subscription', '0012_remove_moved_models_from_app_subscription'),
        ('community', '0013_alter_communitygroupaccess_unique_together'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.CreateModel(
                    name='StorageUsage',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('file_path', models.CharField(help_text='MinIO object path', max_length=500)),
                        ('file_size', models.BigIntegerField(help_text='File size in bytes')),
                        ('file_type', models.CharField(choices=[('avatar', 'Avatar'), ('banner', 'Banner'), ('classroom_content', 'Classroom Content'), ('classroom_attachment', 'Classroom Attachment'), ('forum_attachment', 'Forum Attachment'), ('post_attachment', 'Post Attachment'), ('quiz_file', 'Quiz File'), ('blog_image', 'Blog Image'), ('featured_content', 'Featured Content'), ('other', 'Other')], default='other', max_length=50)),
                        ('parent_entity_type', models.CharField(blank=True, help_text='Type of parent entity (e.g. Classroom, Post)', max_length=100, null=True)),
                        ('parent_entity_id', models.PositiveBigIntegerField(blank=True, help_text='ID of the parent entity', null=True)),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('community', models.ForeignKey(blank=True, help_text='Community this file belongs to (null for user profile files)', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='storage_usage', to='community.community')),
                        ('owner', models.ForeignKey(help_text='Community owner (for per-owner storage limits)', on_delete=django.db.models.deletion.CASCADE, related_name='storage_usage', to=settings.AUTH_USER_MODEL)),
                    ],
                    options={
                        'verbose_name': 'Storage Usage',
                        'verbose_name_plural': 'Storage Usage',
                        'db_table': 'StorageUsage',
                        'indexes': [
                            models.Index(fields=['owner'], name='StorageUsag_owner_i_4df10b_idx'),
                            models.Index(fields=['community', 'owner'], name='StorageUsag_communi_9dd573_idx'),
                            models.Index(fields=['file_path'], name='StorageUsag_file_pa_500c5d_idx'),
                        ],
                    },
                ),
            ],
        ),
    ]
