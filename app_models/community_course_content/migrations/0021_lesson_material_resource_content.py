from django.db import migrations, models
import django.db.models.deletion


def purge_non_pointer_materials(apps, schema_editor):
    Attachment = apps.get_model('community_course_content', 'LessonDefinitionAttachment')
    Attachment.objects.exclude(kind='supplement').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('community_course_content', '0020_companion_attachment_extract'),
        ('community_resource', '0014_communitydriveconnection_drive_folder'),
    ]

    operations = [
        migrations.AddField(
            model_name='lessondefinitionattachment',
            name='resource_content',
            field=models.ForeignKey(
                blank=True,
                help_text='Drive-backed library file when kind=file. Null for supplements.',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='lesson_attachments',
                to='community_resource.resourcecontent',
            ),
        ),
        migrations.AddConstraint(
            model_name='lessondefinitionattachment',
            constraint=models.UniqueConstraint(
                condition=models.Q(('resource_content__isnull', False)),
                fields=('lesson_definition', 'resource_content'),
                name='uniq_ld_att_resource_content',
            ),
        ),
        migrations.RunPython(purge_non_pointer_materials, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='lessondefinitionattachment',
            name='kind',
            field=models.CharField(
                choices=[('file', 'File'), ('supplement', 'Supplement')],
                help_text='file (Drive resource pointer) or supplement (notes overlay)',
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name='lessondefinitionattachment',
            name='url',
            field=models.TextField(blank=True, help_text='Storage ref for supplements', null=True),
        ),
        migrations.AlterField(
            model_name='lessondefinitionattachment',
            name='content_source',
            field=models.CharField(
                blank=True,
                help_text='Unused for Drive pointers',
                max_length=50,
                null=True,
            ),
        ),
    ]
