from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community_store', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='storepurchase',
            name='external_payment_id',
        ),
        migrations.AddField(
            model_name='storepurchase',
            name='stripe_checkout_session_id',
            field=models.CharField(
                blank=True,
                help_text='Stripe Checkout Session id, if the product is sold via Checkout',
                max_length=255,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='storepurchase',
            name='stripe_customer_id',
            field=models.CharField(
                blank=True,
                help_text='Stripe Customer id for the buyer (optional; useful for logged-in or returning buyers)',
                max_length=255,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='storepurchase',
            name='stripe_payment_intent_id',
            field=models.CharField(
                blank=True,
                help_text='Stripe PaymentIntent id for this checkout',
                max_length=255,
                null=True,
            ),
        ),
        migrations.AddIndex(
            model_name='storepurchase',
            index=models.Index(fields=['stripe_payment_intent_id'], name='StorePurchase_stripe_pi_idx'),
        ),
        migrations.AddIndex(
            model_name='storepurchase',
            index=models.Index(fields=['stripe_checkout_session_id'], name='StorePurchase_stripe_cs_idx'),
        ),
    ]
