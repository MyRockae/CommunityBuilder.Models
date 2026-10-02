from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community_course_content', '0018_companionindexoutbox'),
    ]

    operations = [
        migrations.AddField(
            model_name='lessondefinition',
            name='transcript_status',
            field=models.CharField(
                choices=[
                    ('none', 'None'),
                    ('queued', 'Queued'),
                    ('ready', 'Ready'),
                    ('failed', 'Failed'),
                    ('skipped', 'Skipped'),
                ],
                default='none',
                help_text='Bunny caption / Companion transcript readiness for this lesson',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='lessondefinition',
            name='transcript_language',
            field=models.CharField(blank=True, default='en', max_length=8),
        ),
        migrations.AddField(
            model_name='lessondefinition',
            name='transcript_error',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='companionindexoutbox',
            name='event',
            field=models.CharField(
                choices=[
                    ('upsert', 'upsert'),
                    ('delete', 'delete'),
                    ('invalidate_transcript', 'invalidate_transcript'),
                ],
                max_length=24,
            ),
        ),
        migrations.CreateModel(
            name='CompanionTranscriptJob',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bunny_video_id', models.CharField(max_length=36)),
                ('language', models.CharField(default='en', max_length=8)),
                ('status', models.CharField(
                    choices=[
                        ('claimed', 'claimed'),
                        ('queued', 'queued'),
                        ('uncertain', 'uncertain'),
                        ('ready', 'ready'),
                        ('failed', 'failed'),
                    ],
                    db_index=True,
                    default='claimed',
                    max_length=16,
                )),
                ('attempt_count', models.PositiveIntegerField(default=0)),
                ('claimed_at', models.DateTimeField(blank=True, null=True)),
                ('posted_at', models.DateTimeField(blank=True, null=True)),
                ('last_error', models.TextField(blank=True, default='')),
                ('source_lesson_definition_id', models.BigIntegerField()),
                ('cues_json', models.JSONField(blank=True, default=list)),
                ('caption_version', models.IntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'CompanionTranscriptJob',
            },
        ),
        migrations.AddConstraint(
            model_name='companiontranscriptjob',
            constraint=models.UniqueConstraint(
                fields=('bunny_video_id', 'language'),
                name='companion_transcript_job_video_lang',
            ),
        ),
        migrations.AddIndex(
            model_name='companiontranscriptjob',
            index=models.Index(fields=['status', 'updated_at'], name='companion_txjob_status_idx'),
        ),
    ]
