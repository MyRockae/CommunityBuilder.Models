from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community_course_content', '0017_alter_courselessonplacement_is_preview_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanionIndexOutbox',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.CharField(choices=[('upsert', 'upsert'), ('delete', 'delete')], max_length=16)),
                ('community_id', models.BigIntegerField()),
                ('lesson_definition_id', models.BigIntegerField()),
                ('content_version', models.CharField(blank=True, default='', max_length=64)),
                ('status', models.CharField(choices=[('pending', 'pending'), ('complete', 'complete'), ('failed', 'failed')], db_index=True, default='pending', max_length=16)),
                ('last_error', models.TextField(blank=True, default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'CompanionIndexOutbox',
                'ordering': ['id'],
            },
        ),
        migrations.AddIndex(
            model_name='companionindexoutbox',
            index=models.Index(fields=['status', 'created_at'], name='companion_outbox_status_idx'),
        ),
        migrations.AddIndex(
            model_name='companionindexoutbox',
            index=models.Index(fields=['lesson_definition_id', 'status'], name='companion_outbox_lesson_idx'),
        ),
    ]
