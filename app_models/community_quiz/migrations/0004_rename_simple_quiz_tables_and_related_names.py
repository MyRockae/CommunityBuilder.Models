# Rename physical tables Quiz -> SimpleQuiz, QuizSubmission -> SimpleQuizSubmission.
# related_name changes are state-only (no DB schema change).

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community_quiz', '0003_simple_quiz_rename_and_submission_retention'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='simplequiz',
            table='SimpleQuiz',
        ),
        migrations.AlterModelTable(
            name='simplequizsubmission',
            table='SimpleQuizSubmission',
        ),
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterField(
                    model_name='simplequiz',
                    name='community',
                    field=models.ForeignKey(
                        help_text='Community this quiz belongs to',
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='simple_quizzes',
                        to='community.community',
                    ),
                ),
                migrations.AlterField(
                    model_name='simplequiz',
                    name='payment_plans',
                    field=models.ManyToManyField(
                        blank=True,
                        help_text='Community groups (tiers) that have access to this quiz. Owners and co-owners have access regardless of tier.',
                        related_name='simple_quizzes',
                        to='community.communitygroup',
                    ),
                ),
                migrations.AlterField(
                    model_name='simplequizsubmission',
                    name='user',
                    field=models.ForeignKey(
                        help_text='User who submitted the quiz',
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='simple_quiz_submissions',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
