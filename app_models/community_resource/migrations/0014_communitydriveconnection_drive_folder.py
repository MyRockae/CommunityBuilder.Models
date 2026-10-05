from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community_resource', '0013_community_drive_connection'),
    ]

    operations = [
        migrations.AddField(
            model_name='communitydriveconnection',
            name='drive_folder_id',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Google Drive folder id for new resource uploads',
                max_length=128,
            ),
        ),
        migrations.AddField(
            model_name='communitydriveconnection',
            name='drive_folder_name',
            field=models.CharField(blank=True, default='', max_length=512),
        ),
    ]
