# Generated manually for store product kinds, StoreProductPrice, bookable meeting schema.

import django.core.validators
import django.db.models.deletion
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
from django.db.models import Q


def backfill_store_product_prices(apps, schema_editor):
    StoreProduct = apps.get_model('community_store', 'StoreProduct')
    StoreProductPrice = apps.get_model('community_store', 'StoreProductPrice')
    for p in StoreProduct.objects.all():
        amt = getattr(p, 'amount', None)
        if amt is not None and StoreProductPrice.objects.filter(store_product_id=p.pk, currency__iexact='USD').exists():
            continue
        if amt is not None:
            StoreProductPrice.objects.create(
                store_product_id=p.pk,
                currency='USD',
                amount=amt,
            )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('community_store', '0005_rename_storepurchase_paystack_ref_idx_storepurcha_paystac_185d60_idx_and_more'),
        ('community_meetings', '0004_rename_payment_plans_m2m_to_community_groups'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='storeproduct',
            name='product_kind',
            field=models.CharField(
                choices=[('file', 'File download'), ('link', 'External link'), ('meeting', 'Bookable meeting')],
                db_index=True,
                default='file',
                help_text='How the product is delivered after purchase',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='storeproduct',
            name='external_url',
            field=models.URLField(
                blank=True,
                help_text='Customer-facing URL when product_kind is link',
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='storeproduct',
            name='template_meeting',
            field=models.ForeignKey(
                blank=True,
                help_text='Optional fixed meeting to sell access to (MVP); native scheduling uses bookable settings',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='store_products_ticket',
                to='community_meetings.meeting',
            ),
        ),
        migrations.AlterField(
            model_name='storeproduct',
            name='file_url',
            field=models.URLField(
                blank=True,
                help_text='URL of the downloadable file (required when product_kind is file)',
                null=True,
            ),
        ),
        migrations.CreateModel(
            name='StoreProductPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency', models.CharField(help_text='ISO 4217 code (e.g. USD, NGN, GBP)', max_length=3)),
                (
                    'amount',
                    models.DecimalField(
                        decimal_places=2,
                        help_text='List price in major units of this currency',
                        max_digits=10,
                        validators=[django.core.validators.MinValueValidator(Decimal('0.00'))],
                    ),
                ),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                (
                    'store_product',
                    models.ForeignKey(
                        help_text='Product this price applies to',
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='prices',
                        to='community_store.storeproduct',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Store product price',
                'verbose_name_plural': 'Store product prices',
                'db_table': 'StoreProductPrice',
            },
        ),
        migrations.AddConstraint(
            model_name='storeproductprice',
            constraint=models.UniqueConstraint(
                fields=('store_product', 'currency'),
                name='storeproductprice_unique_product_currency',
            ),
        ),
        migrations.AddIndex(
            model_name='storeproductprice',
            index=models.Index(fields=['store_product', 'currency'], name='StoreProduc_store_pr_idx'),
        ),
        migrations.RunPython(backfill_store_product_prices, noop_reverse),
        migrations.AlterField(
            model_name='storeproduct',
            name='amount',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Legacy list price; prefer StoreProductPrice rows per currency',
                max_digits=10,
                null=True,
                validators=[django.core.validators.MinValueValidator(Decimal('0.00'))],
            ),
        ),
        migrations.AddField(
            model_name='storepurchase',
            name='booked_meeting',
            field=models.ForeignKey(
                blank=True,
                help_text='Meeting created or linked after successful payment for meeting products',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='store_purchases',
                to='community_meetings.meeting',
            ),
        ),
        migrations.AddField(
            model_name='storepurchase',
            name='booked_slot_start_utc',
            field=models.DateTimeField(
                blank=True,
                help_text='When product_kind is meeting: UTC start of the slot purchased (optional for MVP fixed meeting)',
                null=True,
            ),
        ),
        migrations.AddIndex(
            model_name='storepurchase',
            index=models.Index(fields=['booked_slot_start_utc'], name='StorePurcha_booked__idx'),
        ),
        migrations.CreateModel(
            name='StoreBookableMeetingSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'time_zone',
                    models.CharField(
                        default='UTC',
                        help_text='IANA timezone for interpreting weekly availability windows',
                        max_length=64,
                    ),
                ),
                (
                    'duration_minutes',
                    models.PositiveIntegerField(
                        default=30,
                        help_text='Length of each bookable slot',
                        validators=[django.core.validators.MinValueValidator(1)],
                    ),
                ),
                (
                    'buffer_before_minutes',
                    models.PositiveIntegerField(default=0, help_text='Unbookable gap before each slot'),
                ),
                (
                    'buffer_after_minutes',
                    models.PositiveIntegerField(default=0, help_text='Unbookable gap after each slot'),
                ),
                (
                    'minimum_notice_minutes',
                    models.PositiveIntegerField(
                        default=120,
                        help_text='Do not offer slots starting sooner than this many minutes from now',
                    ),
                ),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                (
                    'store_product',
                    models.OneToOneField(
                        help_text='Meeting product these settings belong to',
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='bookable_meeting_settings',
                        to='community_store.storeproduct',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Store bookable meeting settings',
                'verbose_name_plural': 'Store bookable meeting settings',
                'db_table': 'StoreBookableMeetingSettings',
            },
        ),
        migrations.CreateModel(
            name='StoreOwnerAvailabilityWindow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'weekday',
                    models.PositiveSmallIntegerField(
                        help_text='ISO weekday 1=Monday … 7=Sunday',
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(7),
                        ],
                    ),
                ),
                (
                    'local_start',
                    models.TimeField(help_text='Start of availability in settings.time_zone'),
                ),
                (
                    'local_end',
                    models.TimeField(help_text='End of availability in settings.time_zone'),
                ),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                (
                    'settings',
                    models.ForeignKey(
                        help_text='Bookable settings this window belongs to',
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='windows',
                        to='community_store.storebookablemeetingsettings',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Store owner availability window',
                'verbose_name_plural': 'Store owner availability windows',
                'db_table': 'StoreOwnerAvailabilityWindow',
            },
        ),
        migrations.AddConstraint(
            model_name='storeowneravailabilitywindow',
            constraint=models.CheckConstraint(
                condition=Q(weekday__gte=1, weekday__lte=7),
                name='store_avail_window_weekday_1_7',
            ),
        ),
        migrations.AddIndex(
            model_name='storeowneravailabilitywindow',
            index=models.Index(fields=['settings', 'weekday'], name='StoreOwnerA_setting_idx'),
        ),
        migrations.CreateModel(
            name='StoreProductSlotHold',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'slot_start_utc',
                    models.DateTimeField(db_index=True, help_text='Slot start in UTC'),
                ),
                (
                    'status',
                    models.CharField(
                        choices=[
                            ('pending', 'Pending'),
                            ('converted', 'Converted to purchase'),
                            ('released', 'Released'),
                        ],
                        db_index=True,
                        default='pending',
                        max_length=20,
                    ),
                ),
                (
                    'hold_until',
                    models.DateTimeField(help_text='When this hold expires if checkout does not complete'),
                ),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                (
                    'buyer_user',
                    models.ForeignKey(
                        help_text='User who reserved the slot',
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='store_product_slot_holds',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    'store_product',
                    models.ForeignKey(
                        help_text='Product the slot belongs to',
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='slot_holds',
                        to='community_store.storeproduct',
                    ),
                ),
                (
                    'store_purchase',
                    models.ForeignKey(
                        blank=True,
                        help_text='Purchase row created for this checkout when applicable',
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='slot_holds',
                        to='community_store.storepurchase',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Store product slot hold',
                'verbose_name_plural': 'Store product slot holds',
                'db_table': 'StoreProductSlotHold',
            },
        ),
        migrations.AddConstraint(
            model_name='storeproductslothold',
            constraint=models.UniqueConstraint(
                condition=Q(status='pending'),
                fields=('store_product', 'slot_start_utc'),
                name='store_slothold_unique_pending_slot',
            ),
        ),
        migrations.AddIndex(
            model_name='storeproductslothold',
            index=models.Index(
                fields=['store_product', 'status', 'hold_until'],
                name='StoreProduc_store_pr_0f1b2c_idx',
            ),
        ),
        migrations.AddIndex(
            model_name='storeproduct',
            index=models.Index(fields=['store', 'product_kind'], name='StoreProduct_store_pr_idx'),
        ),
    ]
