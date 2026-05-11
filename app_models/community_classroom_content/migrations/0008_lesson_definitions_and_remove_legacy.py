# Data migration: ClassroomContent -> LessonDefinition + ClassroomLessonPlacement

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


def forwards_migrate_lesson_data(apps, schema_editor):
    ClassroomContent = apps.get_model('community_classroom_content', 'ClassroomContent')
    ClassroomAttachment = apps.get_model('community_classroom_content', 'ClassroomAttachment')
    ClassroomResource = apps.get_model('community_classroom_content', 'ClassroomResource')
    ClassroomContentCompletion = apps.get_model('community_classroom_content', 'ClassroomContentCompletion')
    LessonDefinition = apps.get_model('community_classroom_content', 'LessonDefinition')
    ClassroomLessonPlacement = apps.get_model('community_classroom_content', 'ClassroomLessonPlacement')
    LessonDefinitionAttachment = apps.get_model('community_classroom_content', 'LessonDefinitionAttachment')
    LessonPlacementCompletion = apps.get_model('community_classroom_content', 'LessonPlacementCompletion')

    cc_to_ld = {}
    cc_to_placement = {}

    for cc in ClassroomContent.objects.all().order_by('id'):
        community_id = cc.classroom.community_id
        ld = LessonDefinition.objects.create(
            community_id=community_id,
            title=cc.title,
            description=cc.description,
            notes=cc.notes,
            content_url=cc.content_url,
            thumbnail_url=cc.thumbnail_url,
            content_source=cc.content_source,
        )
        cc_to_ld[cc.id] = ld.id
        pl = ClassroomLessonPlacement.objects.create(
            classroom_id=cc.classroom_id,
            lesson_definition_id=ld.id,
            order=cc.order,
        )
        cc_to_placement[cc.id] = pl.id

    for att in ClassroomAttachment.objects.all().order_by('content_id', 'created_at', 'id'):
        ld_id = cc_to_ld.get(att.content_id)
        if not ld_id:
            continue
        n = LessonDefinitionAttachment.objects.filter(lesson_definition_id=ld_id).count()
        LessonDefinitionAttachment.objects.create(
            lesson_definition_id=ld_id,
            title=(att.description or 'Supplement')[:255],
            kind='supplement',
            url=att.file_url,
            supplement_file_type=att.file_type,
            description=att.description,
            order=n,
        )

    for res in ClassroomResource.objects.all().order_by('order', 'id'):
        ld_id = cc_to_ld.get(res.content_id)
        if not ld_id:
            continue
        LessonDefinitionAttachment.objects.create(
            lesson_definition_id=ld_id,
            title=res.title,
            kind=res.kind,
            url=res.url,
            content_source=res.content_source,
            order=res.order,
        )

    for comp in ClassroomContentCompletion.objects.all():
        placement_id = cc_to_placement.get(comp.content_id)
        if not placement_id:
            continue
        LessonPlacementCompletion.objects.get_or_create(
            placement_id=placement_id,
            user_id=comp.user_id,
            defaults={'completed_at': comp.completed_at},
        )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('community_classroom_content', '0007_rename_classroomreso_content_91e711_idx_classroomre_content_78118c_idx_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='LessonDefinition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Title of the lesson', max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('content_url', models.URLField(blank=True, null=True)),
                ('thumbnail_url', models.URLField(blank=True, null=True)),
                ('content_source', models.CharField(blank=True, max_length=50, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                (
                    'community',
                    models.ForeignKey(
                        help_text='Community this lesson definition belongs to',
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='lesson_definitions',
                        to='community.community',
                    ),
                ),
            ],
            options={
                'db_table': 'LessonDefinition',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ClassroomLessonPlacement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField(default=0, help_text='Order within this classroom (lower first)')),
                (
                    'classroom',
                    models.ForeignKey(
                        help_text='Classroom syllabus',
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='lesson_placements',
                        to='community_classroom.classroom',
                    ),
                ),
                (
                    'lesson_definition',
                    models.ForeignKey(
                        help_text='Canonical lesson row',
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='placements',
                        to='community_classroom_content.lessondefinition',
                    ),
                ),
            ],
            options={
                'db_table': 'ClassroomLessonPlacement',
                'ordering': ['order', '-id'],
            },
        ),
        migrations.AddConstraint(
            model_name='classroomlessonplacement',
            constraint=models.UniqueConstraint(
                fields=('classroom', 'lesson_definition'),
                name='uniq_classroom_lessondefinition_placement',
            ),
        ),
        migrations.CreateModel(
            name='LessonDefinitionAttachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Display title or label', max_length=255)),
                (
                    'kind',
                    models.CharField(
                        choices=[
                            ('link', 'Link'),
                            ('file', 'File'),
                            ('video', 'Video'),
                            ('supplement', 'Supplement'),
                        ],
                        max_length=20,
                    ),
                ),
                ('url', models.TextField(blank=True, null=True)),
                ('content_source', models.CharField(blank=True, max_length=50, null=True)),
                ('supplement_file_type', models.CharField(blank=True, max_length=10, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('order', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                (
                    'lesson_definition',
                    models.ForeignKey(
                        help_text='Lesson this row belongs to',
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='attachments',
                        to='community_classroom_content.lessondefinition',
                    ),
                ),
            ],
            options={
                'db_table': 'LessonDefinitionAttachment',
                'ordering': ['order', 'id'],
            },
        ),
        migrations.CreateModel(
            name='LessonPlacementCompletion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('completed_at', models.DateTimeField(default=django.utils.timezone.now)),
                (
                    'placement',
                    models.ForeignKey(
                        help_text='Syllabus row completed',
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='completions',
                        to='community_classroom_content.classroomlessonplacement',
                    ),
                ),
                (
                    'user',
                    models.ForeignKey(
                        help_text='User who completed',
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='lesson_placement_completions',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'db_table': 'LessonPlacementCompletion',
                'ordering': ['-completed_at'],
                'unique_together': {('placement', 'user')},
            },
        ),
        migrations.RunPython(forwards_migrate_lesson_data, noop_reverse),
        migrations.DeleteModel(name='ClassroomResource'),
        migrations.DeleteModel(name='ClassroomAttachment'),
        migrations.DeleteModel(name='ClassroomContentCompletion'),
        migrations.DeleteModel(name='ClassroomContent'),
    ]
