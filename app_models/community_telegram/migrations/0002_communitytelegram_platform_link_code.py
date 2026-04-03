from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community_telegram', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='communitytelegram',
            name='platform_link_code',
            field=models.CharField(
                blank=True,
                db_index=True,
                help_text='Short-lived code; owner posts /link <code> in the group with the platform bot.',
                max_length=40,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='communitytelegram',
            name='platform_link_code_expires',
            field=models.DateTimeField(
                blank=True,
                help_text='When platform_link_code stops being valid.',
                null=True,
            ),
        ),
    ]
