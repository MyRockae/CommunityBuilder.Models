import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_subscription', '0004_alter_communitymembersubscription_unique_together'),
        ('community_store', '0002_storepurchase_stripe_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymenttransaction',
            name='store_purchase',
            field=models.ForeignKey(
                blank=True,
                help_text='Store product purchase (if transaction_type is store_purchase)',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='payment_transactions',
                to='community_store.storepurchase',
            ),
        ),
        migrations.AddIndex(
            model_name='paymenttransaction',
            index=models.Index(fields=['store_purchase', 'status'], name='PaymentTran_store_p_idx'),
        ),
    ]
