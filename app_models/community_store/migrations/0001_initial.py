import uuid

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def create_stores_for_existing_communities(apps, schema_editor):
    Community = apps.get_model('community', 'Community')
    CommunityStore = apps.get_model('community_store', 'CommunityStore')
    for community in Community.objects.all():
        CommunityStore.objects.get_or_create(community_id=community.pk)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('community', '0013_alter_communitygroupaccess_unique_together'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CommunityStore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True, help_text='If false, the store is hidden or disabled.')),
                (
                    'download_link_expiry_hours',
                    models.PositiveIntegerField(
                        default=72,
                        help_text='Default lifetime for product download links sent by email (hours). API may override per token.',
                    ),
                ),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                (
                    'community',
                    models.OneToOneField(
                        help_text='Community that owns this store',
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='store',
                        to='community.community',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Community Store',
                'verbose_name_plural': 'Community Stores',
                'db_table': 'CommunityStore',
            },
        ),
        migrations.CreateModel(
            name='StoreProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Display name of the digital product', max_length=255)),
                (
                    'summary',
                    models.CharField(
                        blank=True,
                        help_text='Short summary shown in listings',
                        max_length=500,
                        null=True,
                    ),
                ),
                (
                    'description',
                    models.TextField(blank=True, help_text='Selling points / what the product is about', null=True),
                ),
                (
                    'amount',
                    models.DecimalField(
                        decimal_places=2,
                        help_text='Price charged for the product',
                        max_digits=10,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                (
                    'thumbnail_url',
                    models.URLField(blank=True, help_text='Cover image (e.g. book cover)', null=True),
                ),
                (
                    'banner_url',
                    models.URLField(blank=True, help_text='Banner image for the product page', null=True),
                ),
                ('file_url', models.URLField(help_text='URL of the downloadable product file')),
                (
                    'notes',
                    models.TextField(blank=True, help_text='How to use the product (text)', null=True),
                ),
                (
                    'file_note_url',
                    models.URLField(
                        blank=True,
                        help_text='Optional instructions file (PDF, Word, image) when text notes are not used',
                        null=True,
                    ),
                ),
                (
                    'is_active',
                    models.BooleanField(default=True, help_text='Inactive products can be hidden from the storefront'),
                ),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                (
                    'listed_by',
                    models.ForeignKey(
                        blank=True,
                        help_text='User who uploaded / listed the product',
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='listed_store_products',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    'store',
                    models.ForeignKey(
                        help_text='Store this product belongs to',
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='products',
                        to='community_store.communitystore',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Store Product',
                'verbose_name_plural': 'Store Products',
                'db_table': 'StoreProduct',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='StorePurchase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'buyer_email',
                    models.EmailField(help_text='Buyer email (normalized to lower case on save)', max_length=254),
                ),
                (
                    'status',
                    models.CharField(
                        choices=[
                            ('pending', 'Pending payment'),
                            ('completed', 'Completed'),
                            ('failed', 'Failed'),
                            ('refunded', 'Refunded'),
                        ],
                        default='pending',
                        max_length=20,
                    ),
                ),
                (
                    'amount_paid',
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text='Amount actually charged (snapshot at completion)',
                        max_digits=10,
                        null=True,
                    ),
                ),
                (
                    'currency',
                    models.CharField(default='USD', help_text='ISO 4217 currency code', max_length=3),
                ),
                (
                    'external_payment_id',
                    models.CharField(
                        blank=True,
                        help_text='Payment provider reference (e.g. Stripe PaymentIntent or Checkout Session id)',
                        max_length=255,
                        null=True,
                    ),
                ),
                (
                    'purchased_at',
                    models.DateTimeField(blank=True, help_text='When payment succeeded', null=True),
                ),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                (
                    'buyer_user',
                    models.ForeignKey(
                        blank=True,
                        help_text='Logged-in buyer, if any',
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='store_purchases',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    'product',
                    models.ForeignKey(
                        help_text='Product being purchased',
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='purchases',
                        to='community_store.storeproduct',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Store Purchase',
                'verbose_name_plural': 'Store Purchases',
                'db_table': 'StorePurchase',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='StoreDownloadToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('expires_at', models.DateTimeField(help_text='When the download link stops working')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                (
                    'purchase',
                    models.ForeignKey(
                        help_text='Purchase this download link is tied to',
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='download_tokens',
                        to='community_store.storepurchase',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Store Download Token',
                'verbose_name_plural': 'Store Download Tokens',
                'db_table': 'StoreDownloadToken',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='storeproduct',
            index=models.Index(fields=['store', 'is_active'], name='StoreProduct_store_id_2a8f91_idx'),
        ),
        migrations.AddIndex(
            model_name='storepurchase',
            index=models.Index(fields=['product', 'buyer_email'], name='StorePurchase_product_0f3c2a_idx'),
        ),
        migrations.AddIndex(
            model_name='storepurchase',
            index=models.Index(fields=['status'], name='StorePurchase_status_8b1d4e_idx'),
        ),
        migrations.AddIndex(
            model_name='storedownloadtoken',
            index=models.Index(fields=['expires_at'], name='StoreDownloadToken_expires_idx'),
        ),
        migrations.AddConstraint(
            model_name='storepurchase',
            constraint=models.UniqueConstraint(
                condition=models.Q(status='completed'),
                fields=('product', 'buyer_email'),
                name='storepurchase_unique_completed_email_per_product',
            ),
        ),
        migrations.RunPython(create_stores_for_existing_communities, noop_reverse),
    ]
