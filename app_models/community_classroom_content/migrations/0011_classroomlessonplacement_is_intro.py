from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community_classroom_content', '0010_lessondefinition_video_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='classroomlessonplacement',
            name='is_intro',
            field=models.BooleanField(
                default=False,
                help_text='When true, this syllabus row is the public intro/preview lesson for the classroom.',
            ),
        ),
    ]
