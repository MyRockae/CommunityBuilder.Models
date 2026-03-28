from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0011_rename_payment_plan_models'),
        ('community_meetings', '0002_meeting_series'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterField(
                    model_name='meeting',
                    name='payment_plans',
                    field=models.ManyToManyField(
                        blank=True,
                        help_text='Community groups (tiers) that have access to this meeting',
                        related_name='meetings',
                        to='community.communitygroup',
                    ),
                ),
                migrations.AlterField(
                    model_name='meetingseries',
                    name='payment_plans',
                    field=models.ManyToManyField(
                        blank=True,
                        help_text='Community groups (tiers) that have access to this series',
                        related_name='meeting_series',
                        to='community.communitygroup',
                    ),
                ),
            ],
        ),
    ]
