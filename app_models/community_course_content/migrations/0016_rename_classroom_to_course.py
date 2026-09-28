# Rename ClassroomLessonPlacement / ClassroomCertificate to Course*.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community_course', '0011_rename_classroom_to_course'),
        ('community_course_content', '0015_rename_is_intro_to_is_preview'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(old_name='ClassroomLessonPlacement', new_name='CourseLessonPlacement'),
        migrations.RenameModel(old_name='ClassroomCertificate', new_name='CourseCertificate'),
        migrations.AlterModelOptions(
            name='courselessonplacement',
            options={
                'ordering': ['order', '-id'],
                'verbose_name': 'Course Lesson Placement',
                'verbose_name_plural': 'Course Lesson Placements',
            },
        ),
        migrations.AlterModelOptions(
            name='coursecertificate',
            options={
                'ordering': ['-issued_at'],
                'verbose_name': 'Course Certificate',
                'verbose_name_plural': 'Course Certificates',
            },
        ),
        migrations.RenameField(model_name='courselessonplacement', old_name='classroom', new_name='course'),
        migrations.RenameField(model_name='coursecertificate', old_name='classroom', new_name='course'),
        migrations.RemoveConstraint(
            model_name='courselessonplacement',
            name='uniq_classroom_lessondefinition_placement',
        ),
        migrations.AddConstraint(
            model_name='courselessonplacement',
            constraint=models.UniqueConstraint(
                fields=('course', 'lesson_definition'),
                name='uniq_course_lessondefinition_placement',
            ),
        ),
        migrations.RemoveIndex(
            model_name='courselessonplacement',
            name='clp_classroom_preview_idx',
        ),
        migrations.RemoveIndex(
            model_name='courselessonplacement',
            name='ClassroomLe_classro_739b78_idx',
        ),
        migrations.RemoveIndex(
            model_name='courselessonplacement',
            name='ClassroomLe_lesson__60fc72_idx',
        ),
        migrations.AddIndex(
            model_name='courselessonplacement',
            index=models.Index(fields=['lesson_definition'], name='clp_lesson_definition_idx'),
        ),
        migrations.AddIndex(
            model_name='courselessonplacement',
            index=models.Index(fields=['course'], name='clp_course_idx'),
        ),
        migrations.AddIndex(
            model_name='courselessonplacement',
            index=models.Index(fields=['course', 'is_preview'], name='clp_course_preview_idx'),
        ),
        migrations.AlterUniqueTogether(name='coursecertificate', unique_together={('course', 'user')}),
        migrations.AlterField(
            model_name='courselessonplacement',
            name='course',
            field=models.ForeignKey(
                help_text='Course syllabus',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='lesson_placements',
                to='community_course.course',
            ),
        ),
        migrations.AlterField(
            model_name='coursecertificate',
            name='course',
            field=models.ForeignKey(
                help_text='Course this certificate is for',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='certificates',
                to='community_course.course',
            ),
        ),
        migrations.AlterField(
            model_name='coursecertificate',
            name='user',
            field=models.ForeignKey(
                help_text='User who received the certificate',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='course_certificates',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
