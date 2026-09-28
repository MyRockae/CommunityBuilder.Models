from django.db import migrations

OLD_TO_NEW = {
    'community_classroom_lessons_completed': 'community_course_lessons_completed',
    'community_classroom_quizzes_passed': 'community_course_quizzes_passed',
}


def rename_classroom_metric_keys(apps, schema_editor):
    UserMetricRollup = apps.get_model('metrics', 'UserMetricRollup')
    for old, new in OLD_TO_NEW.items():
        UserMetricRollup.objects.filter(metric_key=old).update(metric_key=new)


def reverse_classroom_metric_keys(apps, schema_editor):
    UserMetricRollup = apps.get_model('metrics', 'UserMetricRollup')
    for old, new in OLD_TO_NEW.items():
        UserMetricRollup.objects.filter(metric_key=new).update(metric_key=old)


class Migration(migrations.Migration):

    dependencies = [
        ('metrics', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(rename_classroom_metric_keys, reverse_classroom_metric_keys),
    ]
