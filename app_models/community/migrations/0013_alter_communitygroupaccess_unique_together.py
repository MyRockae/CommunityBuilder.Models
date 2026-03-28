from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0012_alter_communitygroup_options_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='communitygroupaccess',
            unique_together={('user', 'community', 'community_group')},
        ),
    ]
