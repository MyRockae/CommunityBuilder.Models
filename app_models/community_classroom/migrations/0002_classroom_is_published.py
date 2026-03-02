from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community_classroom', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='classroom',
            name='is_published',
            field=models.BooleanField(default=False, help_text='If True, the classroom is visible/published to members'),
        ),
    ]

