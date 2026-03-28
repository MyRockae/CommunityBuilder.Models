from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0011_rename_payment_plan_models'),
        ('community_polls', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterField(
                    model_name='poll',
                    name='payment_plans',
                    field=models.ManyToManyField(
                        blank=True,
                        help_text='Community groups (tiers) that have access to this poll. Owners, co-owners, and moderators have access regardless of tier.',
                        related_name='polls',
                        to='community.communitygroup',
                    ),
                ),
            ],
        ),
    ]
