import django
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.db.models import Q


def _payment_checkoutsession_subject_check_constraint():
    q = (
        Q(app_subscription__isnull=False, community_member_subscription__isnull=True, store_purchase__isnull=True)
        | Q(app_subscription__isnull=True, community_member_subscription__isnull=False, store_purchase__isnull=True)
        | Q(app_subscription__isnull=True, community_member_subscription__isnull=True, store_purchase__isnull=False)
    )
    name = 'paymentcheckoutsession_exactly_one_subject'
    if django.VERSION >= (5, 2):
        return models.CheckConstraint(condition=q, name=name)
    return models.CheckConstraint(check=q, name=name)


class Migration(migrations.Migration):

    dependencies = [
        ('app_payments', '0004_alter_payoutprofile_identity_document_number_and_more'),
        ('app_subscription', '0015_alter_appsubscriptiontier_options'),
        ('community_store', '0005_rename_storepurchase_paystack_ref_idx_storepurcha_paystac_185d60_idx_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentCheckoutSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'session_kind',
                    models.CharField(
                        choices=[
                            ('app_subscription', 'App Subscription'),
                            ('community_member_subscription', 'Community Member Subscription'),
                            ('store_purchase', 'Store Product Purchase'),
                        ],
                        help_text='Which subject FK is populated — same vocabulary as PaymentTransaction.transaction_type',
                        max_length=50,
                    ),
                ),
                (
                    'status',
                    models.CharField(
                        choices=[
                            ('pending', 'Pending'),
                            ('completed', 'Completed'),
                            ('expired', 'Expired'),
                            ('revoked', 'Revoked'),
                            ('failed', 'Failed'),
                        ],
                        default='pending',
                        help_text='Lifecycle: pending until completed, expired, revoked, or failed',
                        max_length=20,
                    ),
                ),
                (
                    'token_hash',
                    models.CharField(
                        help_text='Hex digest of opaque checkout token (raw token only sent once in URL)',
                        max_length=64,
                        unique=True,
                    ),
                ),
                (
                    'payment_gateway',
                    models.CharField(
                        blank=True,
                        choices=[('stripe', 'Stripe'), ('paystack', 'Paystack')],
                        help_text='Processor for this checkout (stripe / paystack)',
                        max_length=20,
                        null=True,
                    ),
                ),
                (
                    'metadata',
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text='Optional type-specific context (return URLs, display hints, etc.); do not store client_secret here',
                    ),
                ),
                ('expires_at', models.DateTimeField(help_text='When this session stops accepting exchange')),
                ('used_at', models.DateTimeField(blank=True, help_text='When checkout handoff was consumed or payment completed', null=True)),
                ('revoked_at', models.DateTimeField(blank=True, help_text='When user or system cancelled before completion', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                (
                    'app_subscription',
                    models.ForeignKey(
                        blank=True,
                        help_text='Set when session_kind is app_subscription',
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='payment_checkout_sessions',
                        to='app_subscription.appsubscription',
                    ),
                ),
                (
                    'community_member_subscription',
                    models.ForeignKey(
                        blank=True,
                        help_text='Set when session_kind is community_member_subscription',
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='payment_checkout_sessions',
                        to='app_subscription.communitymembersubscription',
                    ),
                ),
                (
                    'store_purchase',
                    models.ForeignKey(
                        blank=True,
                        help_text='Set when session_kind is store_purchase',
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='payment_checkout_sessions',
                        to='community_store.storepurchase',
                    ),
                ),
                (
                    'user',
                    models.ForeignKey(
                        help_text='Buyer who may redeem this session (must match authenticated user on exchange)',
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='payment_checkout_sessions',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'verbose_name': 'Payment checkout session',
                'verbose_name_plural': 'Payment checkout sessions',
                'db_table': 'PaymentCheckoutSession',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='paymentcheckoutsession',
            index=models.Index(fields=['user', 'status', 'expires_at'], name='PaymentCheck_user_stat_exp_idx'),
        ),
        migrations.AddIndex(
            model_name='paymentcheckoutsession',
            index=models.Index(fields=['status', 'expires_at'], name='PaymentCheck_stat_exp_idx'),
        ),
        migrations.AddIndex(
            model_name='paymentcheckoutsession',
            index=models.Index(fields=['session_kind', 'status'], name='PaymentCheck_kind_stat_idx'),
        ),
        migrations.AddConstraint(
            model_name='paymentcheckoutsession',
            constraint=_payment_checkoutsession_subject_check_constraint(),
        ),
    ]
