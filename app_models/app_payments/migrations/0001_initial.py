# State-only: tables PaymentTransaction and CreatorPayoutAccount already exist (app_subscription).

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('app_subscription', '0011_appsubscriptiontierprice'),
        ('community_store', '0005_rename_storepurchase_paystack_ref_idx_storepurcha_paystac_185d60_idx_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.CreateModel(
                    name='CreatorPayoutAccount',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('payment_gateway', models.CharField(choices=[('stripe', 'Stripe'), ('paystack', 'Paystack')], help_text='Processor this payout account is registered with', max_length=20)),
                        ('label', models.CharField(blank=True, default='', help_text='Optional label shown to the creator (e.g. main bank, NGN wallet)', max_length=255)),
                        ('status', models.CharField(choices=[('pending', 'Pending onboarding'), ('active', 'Active — payouts enabled'), ('restricted', 'Restricted'), ('disabled', 'Disabled')], default='pending', help_text='Onboarding / capability state mirrored from the gateway where possible', max_length=20)),
                        ('is_primary', models.BooleanField(default=False, help_text='Preferred account for this user on this gateway (splits / transfers)')),
                        ('stripe_connect_account_id', models.CharField(blank=True, help_text='Stripe Connect account id (acct_…)', max_length=255, null=True)),
                        ('paystack_subaccount_code', models.CharField(blank=True, help_text='Paystack subaccount code for split settlements', max_length=255, null=True)),
                        ('paystack_recipient_code', models.CharField(blank=True, help_text='Paystack transfer recipient code for payouts to bank/mobile money', max_length=255, null=True)),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                        ('user', models.ForeignKey(help_text='Creator (community owner) receiving payouts', on_delete=django.db.models.deletion.CASCADE, related_name='creator_payout_accounts', to=settings.AUTH_USER_MODEL)),
                    ],
                    options={
                        'verbose_name': 'Creator payout account',
                        'verbose_name_plural': 'Creator payout accounts',
                        'db_table': 'CreatorPayoutAccount',
                        'ordering': ['-is_primary', '-updated_at'],
                        'indexes': [
                            models.Index(fields=['user', 'payment_gateway', 'status'], name='CreatorPayo_user_id_cd8639_idx'),
                            models.Index(fields=['user', 'is_primary'], name='CreatorPayo_user_id_a79758_idx'),
                            models.Index(fields=['stripe_connect_account_id'], name='CreatorPayo_stripe__1fe35b_idx'),
                            models.Index(fields=['paystack_subaccount_code'], name='CreatorPayo_paystac_3d6ee9_idx'),
                        ],
                        'constraints': [
                            models.UniqueConstraint(
                                condition=Q(is_primary=True),
                                fields=('user', 'payment_gateway'),
                                name='creatorpayoutaccount_unique_primary_per_user_gateway',
                            ),
                        ],
                    },
                ),
                migrations.CreateModel(
                    name='PaymentTransaction',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('transaction_type', models.CharField(choices=[('app_subscription', 'App Subscription'), ('community_member_subscription', 'Community Member Subscription'), ('store_purchase', 'Store Product Purchase')], help_text='Type of transaction', max_length=50)),
                        ('total_amount', models.DecimalField(decimal_places=2, help_text='Total payment amount charged to the buyer', max_digits=10)),
                        ('platform_fee', models.DecimalField(decimal_places=2, default=0, help_text='Platform cut (e.g. 2% for community subscriptions and store sales; 0 for app subscriptions)', max_digits=10)),
                        ('owner_amount', models.DecimalField(decimal_places=2, default=0, help_text='Amount owed to the community owner after platform_fee (e.g. 98% for member subs and store sales)', max_digits=10)),
                        ('currency', models.CharField(default='USD', help_text='Currency code (USD, EUR, etc.)', max_length=3)),
                        ('status', models.CharField(choices=[('pending', 'Pending'), ('succeeded', 'Succeeded'), ('failed', 'Failed'), ('refunded', 'Refunded')], default='pending', help_text='Payment status', max_length=20)),
                        ('billing_country', models.CharField(blank=True, help_text='ISO 3166-1 alpha-2 country for this charge', max_length=2, null=True)),
                        ('payment_gateway', models.CharField(blank=True, choices=[('stripe', 'Stripe'), ('paystack', 'Paystack')], help_text='Processor that captured this payment', max_length=20, null=True)),
                        ('stripe_payment_intent_id', models.CharField(blank=True, help_text='Stripe PaymentIntent id (null when payment_gateway is paystack)', max_length=255, null=True, unique=True)),
                        ('stripe_charge_id', models.CharField(blank=True, help_text='Stripe charge ID', max_length=255, null=True)),
                        ('paystack_transaction_reference', models.CharField(blank=True, help_text='Paystack transaction reference (null when payment_gateway is stripe)', max_length=255, null=True, unique=True)),
                        ('transferred_to_owner', models.BooleanField(default=False, help_text='Whether owner_amount has been paid out to the community owner')),
                        ('transferred_at', models.DateTimeField(blank=True, help_text='When the transfer to owner was completed', null=True)),
                        ('stripe_transfer_id', models.CharField(blank=True, help_text='Stripe Transfer id (Connect) or payout reference for owner_amount', max_length=255, null=True)),
                        ('paystack_transfer_reference', models.CharField(blank=True, help_text='Paystack transfer reference when owner_amount is paid out via Paystack', max_length=255, null=True)),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('completed_at', models.DateTimeField(blank=True, help_text='When the payment was completed', null=True)),
                        ('app_subscription', models.ForeignKey(blank=True, help_text='App subscription (if transaction_type is app_subscription)', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='app_subscription.appsubscription')),
                        ('community_member_subscription', models.ForeignKey(blank=True, help_text='Community member subscription (if transaction_type is community_member_subscription)', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='app_subscription.communitymembersubscription')),
                        ('creator_payout_account', models.ForeignKey(blank=True, help_text='Creator payout profile used when transferring owner_amount (audit trail)', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payment_transactions', to='app_payments.creatorpayoutaccount')),
                        ('store_purchase', models.ForeignKey(blank=True, help_text='Store product purchase (if transaction_type is store_purchase)', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payment_transactions', to='community_store.storepurchase')),
                    ],
                    options={
                        'verbose_name': 'Payment Transaction',
                        'verbose_name_plural': 'Payment Transactions',
                        'db_table': 'PaymentTransaction',
                        'ordering': ['-created_at'],
                        'indexes': [
                            models.Index(fields=['app_subscription', 'status'], name='PaymentTran_app_sub_777437_idx'),
                            models.Index(fields=['community_member_subscription', 'status'], name='PaymentTran_communi_914bd6_idx'),
                            models.Index(fields=['store_purchase', 'status'], name='PaymentTran_store_p_60c6da_idx'),
                            models.Index(fields=['stripe_payment_intent_id'], name='PaymentTran_stripe__805ae8_idx'),
                            models.Index(fields=['payment_gateway'], name='PaymentTran_gateway_idx'),
                            models.Index(fields=['transferred_to_owner'], name='PaymentTran_transfe_353555_idx'),
                        ],
                    },
                ),
            ],
        ),
    ]
