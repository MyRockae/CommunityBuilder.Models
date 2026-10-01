from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community_course', '0014_coursebundle_community_groups'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='is_featured',
            field=models.BooleanField(
                default=False,
                help_text='If True, the course is listed on the public featured catalog.',
            ),
        ),
        migrations.AddField(
            model_name='course',
            name='public_preview_scope',
            field=models.CharField(
                choices=[
                    ('none', 'None'),
                    ('entire', 'Entire course'),
                    ('parts', 'Selected lessons'),
                ],
                default='none',
                help_text=(
                    'How guest preview lessons are chosen: none (not shown to visitors), '
                    'entire (every syllabus row is public), or parts (selected rows only). '
                    'New lessons inherit is_preview when this is entire.'
                ),
                max_length=16,
            ),
        ),
    ]
