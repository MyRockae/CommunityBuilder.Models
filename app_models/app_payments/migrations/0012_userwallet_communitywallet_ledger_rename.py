# Generated manually — greenfield wallet cutover
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_payments', '0011_paymenttransaction_event_registration_set_null'),
        ('community', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserWallet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'country',
                    models.CharField(
                        blank=True,
                        help_text='ISO 3166-1 alpha-2 country for checkout/gateway routing (null until set)',
                        max_length=2,
                        null=True,
                    ),
                ),
                (
                    'legal_name',
                    models.CharField(
                        blank=True,
                        default='',
                        help_text='Legal name (person or business) for payout onboarding',
                        max_length=255,
                    ),
                ),
                (
                    'payment_gateway',
                    models.CharField(
                        blank=True,
                        choices=[('stripe', 'Stripe'), ('paystack', 'Paystack')],
                        help_text='Processor this payout destination is registered with (null until payout setup)',
                        max_length=20,
                        null=True,
                    ),
                ),
                (
                    'label',
                    models.CharField(
                        blank=True,
                        default='',
                        help_text='Optional label shown to the user (e.g. main bank, NGN wallet)',
                        max_length=255,
                    ),
                ),
                (
                    'status',
                    models.CharField(
                        choices=[
                            ('pending', 'Pending onboarding'),
                            ('active', 'Active — payouts enabled'),
                            ('restricted', 'Restricted'),
                            ('disabled', 'Disabled'),
                        ],
                        default='pending',
                        help_text='Onboarding / capability state mirrored from the gateway where possible',
                        max_length=20,
                    ),
                ),
                (
                    'is_primary',
                    models.BooleanField(
                        default=False,
                        help_text='Preferred payout account for this user on this gateway',
                    ),
                ),
                (
                    'stripe_connect_account_id',
                    models.CharField(
                        blank=True,
                        help_text='Stripe Connect account id (acct_…)',
                        max_length=255,
                        null=True,
                    ),
                ),
                (
                    'paystack_subaccount_code',
                    models.CharField(
                        blank=True,
                        help_text='Paystack subaccount code for split settlements',
                        max_length=255,
                        null=True,
                    ),
                ),
                (
                    'paystack_recipient_code',
                    models.CharField(
                        blank=True,
                        help_text='Paystack transfer recipient code for payouts to bank/mobile money',
                        max_length=255,
                        null=True,
                    ),
                ),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                (
                    'user',
                    models.ForeignKey(
                        help_text='User this wallet belongs to',
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='wallets',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'verbose_name': 'User wallet',
                'verbose_name_plural': 'User wallets',
                'db_table': 'UserWallet',
                'ordering': ['-is_primary', '-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='CommunityWallet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'country',
                    models.CharField(
                        blank=True,
                        help_text='ISO 3166-1 alpha-2 country for seller payout destination',
                        max_length=2,
                        null=True,
                    ),
                ),
                (
                    'legal_name',
                    models.CharField(
                        blank=True,
                        default='',
                        help_text='Legal name (person or business) for community payout onboarding',
                        max_length=255,
                    ),
                ),
                (
                    'payment_gateway',
                    models.CharField(
                        blank=True,
                        choices=[('stripe', 'Stripe'), ('paystack', 'Paystack')],
                        help_text='Processor this payout destination is registered with',
                        max_length=20,
                        null=True,
                    ),
                ),
                (
                    'label',
                    models.CharField(
                        blank=True,
                        default='',
                        help_text='Optional label for this payout destination',
                        max_length=255,
                    ),
                ),
                (
                    'status',
                    models.CharField(
                        choices=[
                            ('pending', 'Pending onboarding'),
                            ('active', 'Active — payouts enabled'),
                            ('restricted', 'Restricted'),
                            ('disabled', 'Disabled'),
                        ],
                        default='pending',
                        help_text='Onboarding / capability state mirrored from the gateway where possible',
                        max_length=20,
                    ),
                ),
                (
                    'stripe_connect_account_id',
                    models.CharField(
                        blank=True,
                        help_text='Stripe Connect account id (acct_…)',
                        max_length=255,
                        null=True,
                    ),
                ),
                (
                    'paystack_subaccount_code',
                    models.CharField(
                        blank=True,
                        help_text='Paystack subaccount code for split settlements',
                        max_length=255,
                        null=True,
                    ),
                ),
                (
                    'paystack_recipient_code',
                    models.CharField(
                        blank=True,
                        help_text='Paystack transfer recipient code for payouts to bank/mobile money',
                        max_length=255,
                        null=True,
                    ),
                ),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                (
                    'community',
                    models.OneToOneField(
                        help_text='Community this payout wallet belongs to',
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='wallet',
                        to='community.community',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Community wallet',
                'verbose_name_plural': 'Community wallets',
                'db_table': 'CommunityWallet',
            },
        ),
        migrations.AddIndex(
            model_name='userwallet',
            index=models.Index(fields=['user', 'payment_gateway', 'status'], name='UserWallet_user_id_d0e8a1_idx'),
        ),
        migrations.AddIndex(
            model_name='userwallet',
            index=models.Index(fields=['user', 'is_primary'], name='UserWallet_user_id_8f2c01_idx'),
        ),
        migrations.AddIndex(
            model_name='userwallet',
            index=models.Index(fields=['stripe_connect_account_id'], name='UserWallet_stripe__a1b2c3_idx'),
        ),
        migrations.AddIndex(
            model_name='userwallet',
            index=models.Index(fields=['paystack_subaccount_code'], name='UserWallet_paystac_d4e5f6_idx'),
        ),
        migrations.AddConstraint(
            model_name='userwallet',
            constraint=models.UniqueConstraint(
                condition=models.Q(is_primary=True, payment_gateway__isnull=False),
                fields=('user', 'payment_gateway'),
                name='userwallet_unique_primary_per_user_gateway',
            ),
        ),
        migrations.AddIndex(
            model_name='communitywallet',
            index=models.Index(fields=['payment_gateway', 'status'], name='CommunityWa_payment_a1b2c3_idx'),
        ),
        migrations.AddIndex(
            model_name='communitywallet',
            index=models.Index(fields=['stripe_connect_account_id'], name='CommunityWa_stripe__d4e5f6_idx'),
        ),
        migrations.AddIndex(
            model_name='communitywallet',
            index=models.Index(fields=['paystack_subaccount_code'], name='CommunityWa_paystac_g7h8i9_idx'),
        ),
        # Ledger renames
        migrations.RemoveIndex(
            model_name='paymenttransaction',
            name='PaymentTran_transfe_353555_idx',
        ),
        migrations.RenameField(
            model_name='paymenttransaction',
            old_name='owner_amount',
            new_name='community_amount',
        ),
        migrations.RenameField(
            model_name='paymenttransaction',
            old_name='transferred_to_owner',
            new_name='transferred_to_community',
        ),
        migrations.AlterField(
            model_name='paymenttransaction',
            name='community_amount',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text='Amount owed to the community after platform_fee (e.g. 98% for member subs and store sales)',
                max_digits=10,
            ),
        ),
        migrations.AlterField(
            model_name='paymenttransaction',
            name='transferred_to_community',
            field=models.BooleanField(
                default=False,
                help_text='Whether community_amount has been paid out to the community wallet',
            ),
        ),
        migrations.AlterField(
            model_name='paymenttransaction',
            name='transferred_at',
            field=models.DateTimeField(
                blank=True,
                help_text='When the transfer to the community was completed',
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name='paymenttransaction',
            name='stripe_transfer_id',
            field=models.CharField(
                blank=True,
                help_text='Stripe Transfer id (Connect) or payout reference for community_amount',
                max_length=255,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name='paymenttransaction',
            name='paystack_transfer_reference',
            field=models.CharField(
                blank=True,
                help_text='Paystack transfer reference when community_amount is paid out via Paystack',
                max_length=255,
                null=True,
            ),
        ),
        migrations.AddIndex(
            model_name='paymenttransaction',
            index=models.Index(fields=['transferred_to_community'], name='PaymentTran_transfe_c9d0e1_idx'),
        ),
        # Drop old creator payout FK; add community_wallet FK
        migrations.RemoveField(
            model_name='paymenttransaction',
            name='creator_payout_account',
        ),
        migrations.AddField(
            model_name='paymenttransaction',
            name='community_wallet',
            field=models.ForeignKey(
                blank=True,
                help_text='Community wallet used when transferring community_amount (audit trail)',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='payment_transactions',
                to='app_payments.communitywallet',
            ),
        ),
        # Drop old tables
        migrations.DeleteModel(name='CreatorPayoutAccount'),
        migrations.DeleteModel(name='UserFiscalProfile'),
    ]
