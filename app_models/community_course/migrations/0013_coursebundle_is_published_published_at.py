from django.db import migrations, models
from django.db.models import F


def backfill_existing_classrooms(apps, schema_editor):
    CourseBundle = apps.get_model('community_course', 'CourseBundle')
    CourseBundle.objects.filter(published_at__isnull=True).update(
        is_published=True,
        published_at=F('created_at'),
    )


class Migration(migrations.Migration):

    dependencies = [
        ('community_course', '0012_rename_classroomco_communi_13e0d2_idx_coursebundl_communi_736e61_idx_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursebundle',
            name='is_published',
            field=models.BooleanField(
                default=False,
                help_text='If True, the classroom is visible/published to members',
            ),
        ),
        migrations.AddField(
            model_name='coursebundle',
            name='published_at',
            field=models.DateTimeField(
                blank=True,
                help_text='Set once when the classroom is first published; remains set if is_published is toggled off so downstream notifications fire only once.',
                null=True,
            ),
        ),
        migrations.AddIndex(
            model_name='coursebundle',
            index=models.Index(fields=['community', 'is_published'], name='CourseBundl_communi_pub_idx'),
        ),
        migrations.RunPython(backfill_existing_classrooms, migrations.RunPython.noop),
    ]
