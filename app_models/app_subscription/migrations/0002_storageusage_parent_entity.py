from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_subscription', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='storageusage',
            name='parent_entity_type',
            field=models.CharField(blank=True, help_text='Type of parent entity (e.g. Classroom, Post)', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='storageusage',
            name='parent_entity_id',
            field=models.PositiveBigIntegerField(blank=True, help_text='ID of the parent entity', null=True),
        ),
    ]
