from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community_telegram', '0003_split_platform_and_private_chat_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='communitytelegram',
            name='private_link_code',
            field=models.CharField(
                blank=True,
                db_index=True,
                help_text='Short-lived code for linking with the community private bot; owner posts /link <code>.',
                max_length=40,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='communitytelegram',
            name='private_link_code_expires',
            field=models.DateTimeField(
                blank=True,
                help_text='When private_link_code stops being valid.',
                null=True,
            ),
        ),
    ]
