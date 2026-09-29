from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community_resource', '0011_resourcecontent_bunny_thumbnail_file_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='resourcecontent',
            name='activated_at',
            field=models.DateTimeField(
                blank=True,
                help_text='Set once when the content is first activated; remains set if is_active is toggled off so downstream notifications fire only once.',
                null=True,
            ),
        ),
    ]
