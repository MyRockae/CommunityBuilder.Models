from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning_journey', '0003_learning_journey_node_classroom_offerings'),
    ]

    operations = [
        migrations.AddField(
            model_name='learningjourneynode',
            name='layout_x',
            field=models.FloatField(
                blank=True,
                help_text='Editor/preview canvas X (React Flow space); null = use auto-layout',
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='learningjourneynode',
            name='layout_y',
            field=models.FloatField(
                blank=True,
                help_text='Editor/preview canvas Y (React Flow space); null = use auto-layout',
                null=True,
            ),
        ),
    ]
