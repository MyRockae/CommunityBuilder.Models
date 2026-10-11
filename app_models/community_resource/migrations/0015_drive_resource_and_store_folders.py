from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community_resource', '0014_communitydriveconnection_drive_folder'),
    ]

    operations = [
        migrations.RenameField(
            model_name='communitydriveconnection',
            old_name='drive_folder_id',
            new_name='resource_folder_id',
        ),
        migrations.RenameField(
            model_name='communitydriveconnection',
            old_name='drive_folder_name',
            new_name='resource_folder_name',
        ),
        migrations.AlterField(
            model_name='communitydriveconnection',
            name='resource_folder_id',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Google Drive folder id for new resource uploads',
                max_length=128,
            ),
        ),
        migrations.AddField(
            model_name='communitydriveconnection',
            name='store_folder_id',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Google Drive folder id for new store digital downloads',
                max_length=128,
            ),
        ),
        migrations.AddField(
            model_name='communitydriveconnection',
            name='store_folder_name',
            field=models.CharField(blank=True, default='', max_length=512),
        ),
    ]
