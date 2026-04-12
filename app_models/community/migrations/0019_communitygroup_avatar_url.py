from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0018_communitysociallink'),
    ]

    operations = [
        migrations.AddField(
            model_name='communitygroup',
            name='avatar_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
