from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0014_communitygroupprice'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='communitygroup',
            name='fee',
        ),
    ]
