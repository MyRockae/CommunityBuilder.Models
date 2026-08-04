from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_user_verification_email_send_tracking'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='token_version',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Incremented to revoke all outstanding JWTs for this user.',
            ),
        ),
    ]
