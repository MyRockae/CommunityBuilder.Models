from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0009_merge_20260314_1748'),
    ]

    operations = [
        migrations.AddField(
            model_name='community',
            name='is_active',
            field=models.BooleanField(default=True, help_text='If false, the community is hidden or disabled.'),
        ),
        migrations.AddField(
            model_name='community',
            name='flag_count',
            field=models.PositiveIntegerField(default=0, help_text='Number of times the community has been flagged by users.'),
        ),
    ]
