from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community_course_content', '0014_lessondefinition_bunny_thumbnail_file_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='classroomlessonplacement',
            old_name='is_intro',
            new_name='is_preview',
        ),
        migrations.AlterField(
            model_name='classroomlessonplacement',
            name='is_preview',
            field=models.BooleanField(
                default=False,
                help_text='When true, unauthenticated visitors can view this syllabus row (notes and playback) on the public classroom page.',
            ),
        ),
        migrations.AddIndex(
            model_name='classroomlessonplacement',
            index=models.Index(fields=['classroom', 'is_preview'], name='clp_classroom_preview_idx'),
        ),
    ]
