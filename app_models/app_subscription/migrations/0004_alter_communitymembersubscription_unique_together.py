from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_subscription', '0003_rename_community_group_fields'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='communitymembersubscription',
            unique_together={('user', 'community', 'community_group')},
        ),
    ]
