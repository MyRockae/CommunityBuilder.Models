from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community_store', '0014_storeslotsession_long_conference_urls'),
    ]

    operations = [
        migrations.AddField(
            model_name='storeproduct',
            name='drive_file_id',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Google Drive file id when product_kind is file',
                max_length=128,
            ),
        ),
        migrations.AddField(
            model_name='storeproduct',
            name='drive_file_name',
            field=models.CharField(blank=True, default='', max_length=512),
        ),
        migrations.AddField(
            model_name='storeproduct',
            name='drive_mime_type',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='storeproduct',
            name='file_url',
            field=models.URLField(
                blank=True,
                help_text='Unused for Drive-backed file products; kept nullable for legacy rows',
                null=True,
            ),
        ),
    ]
