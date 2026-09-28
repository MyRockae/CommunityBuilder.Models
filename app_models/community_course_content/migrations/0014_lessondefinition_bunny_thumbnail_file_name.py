from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community_course_content', '0013_remove_lessondefinition_legacy_video_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='lessondefinition',
            name='bunny_thumbnail_file_name',
            field=models.CharField(
                blank=True,
                help_text='Bunny CDN thumbnail filename (e.g. thumbnail.jpg)',
                max_length=255,
                null=True,
            ),
        ),
    ]
