from django.db import migrations, models


def rename_classroom_file_types(apps, schema_editor):
    StorageUsage = apps.get_model('storage_usage', 'StorageUsage')
    StorageUsage.objects.filter(file_type='classroom_content').update(file_type='course_content')
    StorageUsage.objects.filter(file_type='classroom_attachment').update(file_type='course_attachment')
    StorageUsage.objects.filter(parent_entity_type='Classroom').update(parent_entity_type='Course')


def reverse_classroom_file_types(apps, schema_editor):
    StorageUsage = apps.get_model('storage_usage', 'StorageUsage')
    StorageUsage.objects.filter(file_type='course_content').update(file_type='classroom_content')
    StorageUsage.objects.filter(file_type='course_attachment').update(file_type='classroom_attachment')
    StorageUsage.objects.filter(parent_entity_type='Course').update(parent_entity_type='Classroom')


class Migration(migrations.Migration):

    dependencies = [
        ('storage_usage', '0002_alter_storageusage_file_path'),
    ]

    operations = [
        migrations.RunPython(rename_classroom_file_types, reverse_classroom_file_types),
        migrations.AlterField(
            model_name='storageusage',
            name='file_type',
            field=models.CharField(
                choices=[
                    ('avatar', 'Avatar'),
                    ('banner', 'Banner'),
                    ('course_content', 'Course Content'),
                    ('course_attachment', 'Course Attachment'),
                    ('forum_attachment', 'Forum Attachment'),
                    ('post_attachment', 'Post Attachment'),
                    ('quiz_file', 'Quiz File'),
                    ('blog_image', 'Blog Image'),
                    ('featured_content', 'Featured Content'),
                    ('other', 'Other'),
                ],
                default='other',
                max_length=50,
            ),
        ),
        migrations.AlterField(
            model_name='storageusage',
            name='parent_entity_type',
            field=models.CharField(
                blank=True,
                help_text='Type of parent entity (e.g. Course, Post)',
                max_length=100,
                null=True,
            ),
        ),
    ]
