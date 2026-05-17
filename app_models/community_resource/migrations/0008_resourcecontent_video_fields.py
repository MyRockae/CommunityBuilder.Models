from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community_resource', '0007_rename_payment_plans_m2m_to_community_groups'),
    ]

    operations = [
        migrations.AddField(
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
                help_text='Adaptive HLS transcode state (video bucket); none for non-video or tier without feature',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='resourcecontent',
            name='hls_manifest_object',
            field=models.CharField(
                blank=True,
                help_text='MinIO object key for master.m3u8 in the video transcode bucket',
                max_length=500,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='resourcecontent',
            name='video_error',
            field=models.TextField(
                blank=True,
                help_text='Last transcode error message when video_status is failed',
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='resourcecontent',
            name='video_job_id',
            field=models.CharField(
                blank=True,
                help_text='VideoService transcode job UUID',
                max_length=36,
                null=True,
            ),
        ),
    ]
