import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_payments', '0012_userwallet_communitywallet_ledger_rename'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserEarning',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'amount',
                    models.DecimalField(
                        decimal_places=2,
                        help_text='Amount owed to the user',
                        max_digits=10,
                    ),
                ),
                (
                    'currency',
                    models.CharField(
                        default='USD',
                        help_text='Currency code (USD, EUR, etc.)',
                        max_length=3,
                    ),
                ),
                (
                    'kind',
                    models.CharField(
                        choices=[('referral', 'Referral')],
                        default='referral',
                        help_text='How this credit was earned',
                        max_length=32,
                    ),
                ),
                (
                    'note',
                    models.CharField(
                        blank=True,
                        default='',
                        help_text='Optional short note shown to the user',
                        max_length=255,
                    ),
                ),
                (
                    'transferred_to_user',
                    models.BooleanField(
                        default=False,
                        help_text='Whether amount has been paid out to the user wallet',
                    ),
                ),
                (
                    'transferred_at',
                    models.DateTimeField(
                        blank=True,
                        help_text='When the transfer to the user was completed',
                        null=True,
                    ),
                ),
                (
                    'stripe_transfer_id',
                    models.CharField(
                        blank=True,
                        help_text='Stripe Transfer id when amount is paid out via Stripe',
                        max_length=255,
                        null=True,
                    ),
                ),
                (
                    'paystack_transfer_reference',
                    models.CharField(
                        blank=True,
                        help_text='Paystack transfer reference when amount is paid out via Paystack',
                        max_length=255,
                        null=True,
                    ),
                ),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                (
                    'user',
                    models.ForeignKey(
                        help_text='User this credit is owed to',
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='earnings',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    'user_wallet',
                    models.ForeignKey(
                        blank=True,
                        help_text='User wallet used when transferring amount (audit trail)',
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='earnings',
                        to='app_payments.userwallet',
                    ),
                ),
            ],
            options={
                'verbose_name': 'User earning',
                'verbose_name_plural': 'User earnings',
                'db_table': 'UserEarning',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='userearning',
            index=models.Index(
                fields=['user', 'transferred_to_user'],
                name='UserEarning_user_id_transf_idx',
            ),
        ),
        migrations.AddIndex(
            model_name='userearning',
            index=models.Index(
                fields=['user', 'currency', '-created_at'],
                name='UserEarning_user_cur_created_idx',
            ),
        ),
    ]
