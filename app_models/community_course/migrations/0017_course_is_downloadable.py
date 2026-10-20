from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community_course', '0016_clear_featured_when_course_on_sale'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='is_downloadable',
            field=models.BooleanField(
                default=False,
                help_text='When true, learners with course access may download lesson videos and materials',
            ),
        ),
    ]
