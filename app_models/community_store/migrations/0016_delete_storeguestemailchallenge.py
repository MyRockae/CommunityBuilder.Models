from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('community_store', '0015_storeproduct_drive_file'),
    ]

    operations = [
        migrations.DeleteModel(
            name='StoreGuestEmailChallenge',
        ),
    ]
