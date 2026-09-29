from django.db import migrations, models
from django.db.models import F


def backfill_published_journeys(apps, schema_editor):
    LearningJourney = apps.get_model('learning_journey', 'LearningJourney')
    LearningJourney.objects.filter(is_published=True, published_at__isnull=True).update(
        published_at=F('created_at'),
    )


class Migration(migrations.Migration):

    dependencies = [
        ('learning_journey', '0005_rename_classroom_to_course'),
    ]

    operations = [
        migrations.AddField(
            model_name='learningjourney',
            name='published_at',
            field=models.DateTimeField(
                blank=True,
                help_text='Set once when the roadmap is first published; remains set if is_published is toggled off so downstream notifications fire only once.',
                null=True,
            ),
        ),
        migrations.RunPython(backfill_published_journeys, migrations.RunPython.noop),
    ]
