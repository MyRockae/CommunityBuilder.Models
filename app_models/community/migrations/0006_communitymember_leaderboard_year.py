from django.db import migrations, models
from django.utils import timezone


def default_leaderboard_year():
    return timezone.now().year


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0005_communitymember_points'),
    ]

    operations = [
        migrations.AddField(
            model_name='communitymember',
            name='leaderboard_year',
            field=models.PositiveSmallIntegerField(
                default=default_leaderboard_year,
                help_text='Year this leaderboard period applies to; points reset when year changes.',
            ),
        ),
    ]
