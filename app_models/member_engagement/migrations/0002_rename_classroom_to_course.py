import django.db.models.deletion
from django.db import migrations, models


def rename_classroom_home_surface(apps, schema_editor):
    EngagementEvent = apps.get_model('member_engagement', 'EngagementEvent')
    EngagementEvent.objects.filter(surface='classroom_home').update(surface='course_home')
    EngagementEvent.objects.filter(resource_type='classroom_content').update(resource_type='course_content')


def reverse_classroom_home_surface(apps, schema_editor):
    EngagementEvent = apps.get_model('member_engagement', 'EngagementEvent')
    EngagementEvent.objects.filter(surface='course_home').update(surface='classroom_home')
    EngagementEvent.objects.filter(resource_type='course_content').update(resource_type='classroom_content')


class Migration(migrations.Migration):

    dependencies = [
        ('community_course', '0011_rename_classroom_to_course'),
        ('member_engagement', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='engagementsession',
            old_name='classroom',
            new_name='course',
        ),
        migrations.AlterField(
            model_name='engagementsession',
            name='course',
            field=models.ForeignKey(
                blank=True,
                help_text='Course context when tracking course surfaces; null for community-only events.',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='engagement_sessions',
                to='community_course.course',
            ),
        ),
        migrations.RunPython(rename_classroom_home_surface, reverse_classroom_home_surface),
        migrations.AlterField(
            model_name='engagementevent',
            name='surface',
            field=models.CharField(
                choices=[
                    ('course_home', 'Course home'),
                    ('lesson', 'Lesson'),
                    ('content', 'Content'),
                    ('material', 'Material'),
                    ('video', 'Video'),
                ],
                max_length=32,
            ),
        ),
    ]
