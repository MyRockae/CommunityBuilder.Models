from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community_resource', '0009_resourcecontent_bunny_video_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='resourcecontent',
            name='hls_manifest_object',
        ),
        migrations.RemoveField(
            model_name='resourcecontent',
            name='video_job_id',
        ),
        migrations.AlterField(
            model_name='resourcecontent',
            name='file_url',
            field=models.URLField(
                help_text='Storage ref or external URL for the file',
            ),
        ),
        migrations.AlterField(
            model_name='resourcecontent',
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
            model_name='resourcecontent',
            name='video_error',
            field=models.TextField(
                blank=True,
                help_text='Last Bunny encode error when video_status is failed',
                null=True,
            ),
        ),
    ]
