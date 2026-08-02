from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community_blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='communityblogpost',
            name='is_published',
            field=models.BooleanField(
                db_index=True,
                default=True,
                help_text='False for TipTap media drafts; True when visible on the public blog',
            ),
        ),
    ]
