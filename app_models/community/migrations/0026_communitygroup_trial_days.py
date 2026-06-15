from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0025_leaderboard_point_award_and_chat_counter'),
    ]

    operations = [
        migrations.AddField(
            model_name='communitygroup',
            name='trial_days',
            field=models.PositiveIntegerField(
                blank=True,
                help_text='Optional free trial length in days for paid tiers. Null or 0 means no trial.',
                null=True,
            ),
        ),
    ]
