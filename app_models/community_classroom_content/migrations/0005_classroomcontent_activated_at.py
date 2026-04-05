from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community_classroom_content', '0004_alter_classroomcontent_content_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='classroomcontent',
            name='activated_at',
            field=models.DateTimeField(
                blank=True,
                help_text='Set once when the content is first activated; remains set if is_active is toggled off so downstream notifications fire only once.',
                null=True,
            ),
        ),
    ]
