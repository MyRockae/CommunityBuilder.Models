from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0027_featuredcommunity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='featuredcommunity',
            name='featured_image_url',
            field=models.URLField(max_length=2048),
        ),
    ]
