from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community_classroom_content', '0012_lessondefinition_bunny_video_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lessondefinition',
            name='hls_manifest_object',
        ),
        migrations.RemoveField(
            model_name='lessondefinition',
            name='video_job_id',
        ),
        migrations.AlterField(
            model_name='lessondefinition',
            name='content_url',
            field=models.URLField(
                blank=True,
                help_text='Storage ref or external URL for non-video files; embeds use a full https URL',
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name='lessondefinition',
            name='video_status',
            field=models.CharField(
                choices=[
                    ('none', 'None'),
                    ('processing', 'Processing'),
                    ('ready', 'Ready'),
                    ('failed', 'Failed'),
                ],
                default='none',
                help_text='Bunny Stream encode state',
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name='lessondefinition',
            name='video_error',
            field=models.TextField(
                blank=True,
                help_text='Last Bunny encode error when video_status is failed',
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name='lessondefinitionattachment',
            name='url',
            field=models.TextField(
                blank=True,
                help_text='External URL or storage ref',
                null=True,
            ),
        ),
    ]
