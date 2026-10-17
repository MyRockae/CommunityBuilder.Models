import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_payments', '0010_paymentcheckoutsession_nullable_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymenttransaction',
            name='event_registration',
            field=models.ForeignKey(
                blank=True,
                help_text='Event registration (if transaction_type is event_registration). Cleared when a finished event is deleted so the charge record stays.',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='payment_transactions',
                to='community_event.eventregistration',
            ),
        ),
    ]
