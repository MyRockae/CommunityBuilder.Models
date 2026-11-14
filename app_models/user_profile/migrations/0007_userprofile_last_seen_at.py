from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0006_useraddress_country_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='last_seen_at',
            field=models.DateTimeField(
                blank=True,
                help_text='When the user was last connected to community chat',
                null=True,
            ),
        ),
    ]
