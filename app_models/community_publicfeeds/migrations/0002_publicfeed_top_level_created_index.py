# Generated for public feed list performance (top-level posts by created_at).

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community_publicfeeds', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='publicfeed',
            index=models.Index(
                fields=['-created_at'],
                name='publicfeeds_top_created_idx',
                condition=models.Q(parent_feed__isnull=True),
            ),
        ),
    ]
