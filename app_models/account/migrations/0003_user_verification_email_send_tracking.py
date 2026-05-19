from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_roles_permissions_and_user_roles'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='verification_email_last_send_status',
            field=models.CharField(
                blank=True,
                choices=[('sent', 'Sent'), ('failed', 'Failed')],
                help_text='Result of the last verification email API send attempt.',
                max_length=10,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='user',
            name='verification_email_last_sent_at',
            field=models.DateTimeField(
                blank=True,
                help_text='When the last verification email send attempt completed.',
                null=True,
            ),
        ),
    ]
