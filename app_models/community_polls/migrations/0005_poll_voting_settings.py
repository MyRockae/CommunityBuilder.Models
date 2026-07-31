# Generated manually for poll voting settings (multi / revote / results).

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community_polls', '0004_rename_payment_plans_m2m_to_community_groups'),
    ]

    operations = [
        migrations.AddField(
            model_name='poll',
            name='allow_multiple_choices',
            field=models.BooleanField(
                default=False,
                help_text='When true, voters may select more than one option',
            ),
        ),
        migrations.AddField(
            model_name='poll',
            name='allow_revote',
            field=models.BooleanField(
                default=True,
                help_text='When true, voters may change their previous selection(s)',
            ),
        ),
        migrations.AddField(
            model_name='poll',
            name='show_results',
            field=models.BooleanField(
                default=True,
                help_text='When true, vote tallies are visible to members',
            ),
        ),
        migrations.AlterUniqueTogether(
            name='pollvote',
            unique_together={('poll', 'user', 'option')},
        ),
    ]
