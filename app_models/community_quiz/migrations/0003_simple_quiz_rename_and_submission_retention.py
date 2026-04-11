# Generated manually: Simple Quiz model renames (same DB tables) + submission history on quiz delete

import django.db.models.deletion
from django.db import migrations, models


def backfill_submission_snapshots(apps, schema_editor):
    SimpleQuizSubmission = apps.get_model('community_quiz', 'SimpleQuizSubmission')
    SimpleQuiz = apps.get_model('community_quiz', 'SimpleQuiz')
    for sub in SimpleQuizSubmission.objects.filter(quiz_id__isnull=False).iterator():
        try:
            q = SimpleQuiz.objects.get(pk=sub.quiz_id)
        except SimpleQuiz.DoesNotExist:
            continue
        SimpleQuizSubmission.objects.filter(pk=sub.pk).update(
            community_id=q.community_id,
            quiz_title_snapshot=q.title or '',
            quiz_id_at_submit=q.pk,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0018_communitysociallink'),
        ('community_quiz', '0002_alter_quiz_payment_plans'),
    ]

    operations = [
        migrations.RenameModel(old_name='Quiz', new_name='SimpleQuiz'),
        migrations.RenameModel(old_name='QuizGenerationJob', new_name='SimpleQuizGenerationJob'),
        migrations.RenameModel(old_name='QuizSubmission', new_name='SimpleQuizSubmission'),
        migrations.AlterModelOptions(
            name='simplequiz',
            options={
                'ordering': ['-created_at'],
                'verbose_name': 'Simple Quiz',
                'verbose_name_plural': 'Simple Quizzes',
            },
        ),
        migrations.AlterModelOptions(
            name='simplequizgenerationjob',
            options={
                'ordering': ['-created_at'],
                'verbose_name': 'Simple Quiz Generation Job',
                'verbose_name_plural': 'Simple Quiz Generation Jobs',
            },
        ),
        migrations.AlterModelOptions(
            name='simplequizsubmission',
            options={
                'ordering': ['-created_at'],
                'verbose_name': 'Simple Quiz Submission',
                'verbose_name_plural': 'Simple Quiz Submissions',
            },
        ),
        migrations.AddField(
            model_name='simplequizsubmission',
            name='community',
            field=models.ForeignKey(
                help_text='Community this attempt belongs to (denormalized for history after quiz delete)',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='simple_quiz_submissions',
                to='community.community',
            ),
        ),
        migrations.AddField(
            model_name='simplequizsubmission',
            name='quiz_title_snapshot',
            field=models.CharField(blank=True, default='', help_text='Quiz title at submission time', max_length=255),
        ),
        migrations.AddField(
            model_name='simplequizsubmission',
            name='quiz_id_at_submit',
            field=models.PositiveIntegerField(blank=True, help_text='Quiz primary key at submission time (for reference after delete)', null=True),
        ),
        migrations.RunPython(backfill_submission_snapshots, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='simplequizsubmission',
            name='community',
            field=models.ForeignKey(
                help_text='Community this attempt belongs to (denormalized for history after quiz delete)',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='simple_quiz_submissions',
                to='community.community',
            ),
        ),
        migrations.AlterField(
            model_name='simplequizsubmission',
            name='quiz',
            field=models.ForeignKey(
                blank=True,
                help_text='Quiz that was submitted (null if the quiz was later deleted)',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='submissions',
                to='community_quiz.simplequiz',
            ),
        ),
    ]
