from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0015_remove_communitygroup_fee'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='communitygroup',
            name='is_free',
        ),
    ]
