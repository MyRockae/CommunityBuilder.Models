# Generated manually for ClassroomResource lesson materials

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community_classroom', '0007_classroom_is_featured'),
        ('community_classroom_content', '0005_classroomcontent_activated_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClassroomResource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Display label for the resource', max_length=255)),
                (
                    'kind',
                    models.CharField(
                        choices=[('link', 'Link'), ('file', 'File'), ('video', 'Video')],
                        help_text='link, file (stored object path), or video (external URL)',
                        max_length=10,
                    ),
                ),
                (
                    'url',
                    models.TextField(
                        blank=True,
                        help_text='External URL for link/video, or MinIO object path for uploaded files',
                        null=True,
                    ),
                ),
                (
                    'content_source',
                    models.CharField(
                        blank=True,
                        help_text='For video kind: e.g. youtube, vimeo (optional)',
                        max_length=50,
                        null=True,
                    ),
                ),
                ('order', models.IntegerField(default=0, help_text='Display order within the content item')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                (
                    'classroom',
                    models.ForeignKey(
                        help_text='Classroom this resource belongs to (must match content.classroom)',
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='classroom_resources',
                        to='community_classroom.classroom',
                    ),
                ),
                (
                    'content',
                    models.ForeignKey(
                        help_text='Classroom content item this resource supplements',
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='classroom_resources',
                        to='community_classroom_content.classroomcontent',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Classroom Resource',
                'verbose_name_plural': 'Classroom Resources',
                'db_table': 'ClassroomResource',
                'ordering': ['order', 'id'],
            },
        ),
        migrations.AddIndex(
            model_name='classroomresource',
            index=models.Index(fields=['content'], name='ClassroomReso_content_91e711_idx'),
        ),
        migrations.AddIndex(
            model_name='classroomresource',
            index=models.Index(fields=['classroom'], name='ClassroomReso_classro_4f8b22_idx'),
        ),
    ]
