import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_payments', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PayoutProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'preferred_payment_gateway',
                    models.CharField(
                        blank=True,
                        choices=[('stripe', 'Stripe'), ('paystack', 'Paystack')],
                        help_text='Preferred processor for payouts when the user has multiple options',
                        max_length=20,
                        null=True,
                    ),
                ),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                (
                    'user',
                    models.OneToOneField(
                        help_text='User this payout profile belongs to',
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='payout_profile',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'verbose_name': 'Payout profile',
                'verbose_name_plural': 'Payout profiles',
                'db_table': 'PayoutProfile',
            },
        ),
    ]
