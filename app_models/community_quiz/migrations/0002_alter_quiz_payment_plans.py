from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0011_rename_payment_plan_models'),
        ('community_quiz', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterField(
                    model_name='quiz',
                    name='payment_plans',
                    field=models.ManyToManyField(
                        blank=True,
                        help_text='Community groups (tiers) that have access to this quiz. Owners and co-owners have access regardless of tier.',
                        related_name='quizzes',
                        to='community.communitygroup',
                    ),
                ),
            ],
        ),
    ]
