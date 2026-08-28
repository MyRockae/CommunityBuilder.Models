from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community_resource', '0010_remove_resourcecontent_legacy_video_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='resourcecontent',
            name='bunny_thumbnail_file_name',
            field=models.CharField(
                blank=True,
                help_text='Bunny CDN thumbnail filename (e.g. thumbnail.jpg)',
                max_length=255,
                null=True,
            ),
        ),
    ]
