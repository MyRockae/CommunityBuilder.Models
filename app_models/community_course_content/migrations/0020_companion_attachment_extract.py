from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community_course_content', '0019_companion_transcript_v2'),
    ]

    operations = [
        migrations.AddField(
            model_name='lessondefinition',
            name='companion_index_revision',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Monotonic Companion index order for this lesson. Not a content hash.',
            ),
        ),
        migrations.AddField(
            model_name='companionindexoutbox',
            name='index_revision',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.CreateModel(
            name='CompanionAttachmentExtractJob',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attachment_id', models.BigIntegerField()),
                ('lesson_definition_id', models.BigIntegerField()),
                ('community_id', models.BigIntegerField()),
                ('file_version', models.CharField(help_text='Storage ref captured at enqueue', max_length=1024)),
                ('filename', models.CharField(blank=True, default='', max_length=255)),
                ('kind', models.CharField(choices=[('pdf', 'pdf'), ('docx', 'docx'), ('pptx', 'pptx')], max_length=8)),
                ('status', models.CharField(
                    choices=[
                        ('pending', 'pending'),
                        ('ready', 'ready'),
                        ('skipped', 'skipped'),
                        ('failed', 'failed'),
                        ('stale', 'stale'),
                    ],
                    db_index=True,
                    default='pending',
                    max_length=16,
                )),
                ('enqueue_index_revision', models.PositiveIntegerField(default=0)),
                ('pages_json', models.JSONField(blank=True, default=list)),
                ('last_error', models.TextField(blank=True, default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'CompanionAttachmentExtractJob',
                'ordering': ['id'],
            },
        ),
        migrations.AddIndex(
            model_name='companionattachmentextractjob',
            index=models.Index(fields=['status', 'id'], name='companion_attjob_status_idx'),
        ),
        migrations.AddIndex(
            model_name='companionattachmentextractjob',
            index=models.Index(fields=['attachment_id', 'status'], name='companion_attjob_att_idx'),
        ),
        migrations.AddIndex(
            model_name='companionattachmentextractjob',
            index=models.Index(fields=['lesson_definition_id', 'status'], name='companion_attjob_lesson_idx'),
        ),
    ]
