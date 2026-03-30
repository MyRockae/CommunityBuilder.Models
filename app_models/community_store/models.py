import uuid
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from app_models.account.models import User
from app_models.app_payments.models import PaymentGateway
from app_models.community.models import Community


class CommunityStore(models.Model):
    """
    Each community has exactly one store (created automatically when the community is created;
    existing communities are backfilled via migration).
    """
    community = models.OneToOneField(
        Community,
        on_delete=models.CASCADE,
        related_name='store',
        help_text='Community that owns this store',
    )
    is_active = models.BooleanField(
        default=True,
        help_text='If false, the store is hidden or disabled.',
    )
    download_link_expiry_hours = models.PositiveIntegerField(
        default=72,
        help_text='Default lifetime for product download links sent by email (hours). API may override per token.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'CommunityStore'
        verbose_name = 'Community Store'
        verbose_name_plural = 'Community Stores'

    def __str__(self):
        return f"Store – {self.community.name}"


class StoreProduct(models.Model):
    """A digital product listed in a community store."""
    store = models.ForeignKey(
        CommunityStore,
        on_delete=models.CASCADE,
        related_name='products',
        help_text='Store this product belongs to',
    )
    name = models.CharField(max_length=255, help_text='Display name of the digital product')
    summary = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text='Short summary shown in listings',
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text='Selling points / what the product is about',
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Price charged for the product',
    )
    thumbnail_url = models.URLField(
        blank=True,
        null=True,
        help_text='Cover image (e.g. book cover)',
    )
    banner_url = models.URLField(
        blank=True,
        null=True,
        help_text='Banner image for the product page',
    )
    listed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='listed_store_products',
        help_text='User who uploaded / listed the product',
    )
    file_url = models.URLField(help_text='URL of the downloadable product file')
    notes = models.TextField(
        blank=True,
        null=True,
        help_text='How to use the product (text)',
    )
    file_note_url = models.URLField(
        blank=True,
        null=True,
        help_text='Optional instructions file (PDF, Word, image) when text notes are not used',
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Inactive products can be hidden from the storefront',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StoreProduct'
        verbose_name = 'Store Product'
        verbose_name_plural = 'Store Products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['store', 'is_active']),
        ]

    def __str__(self):
        return self.name


class StorePurchase(models.Model):
    """
    A checkout / payment record for a product and buyer email.
    At most one completed purchase per (product, buyer_email); repeat buyers get new download links only.
    """
    STATUS_PENDING = 'pending'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'
    STATUS_REFUNDED = 'refunded'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending payment'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_REFUNDED, 'Refunded'),
    ]

    product = models.ForeignKey(
        StoreProduct,
        on_delete=models.CASCADE,
        related_name='purchases',
        help_text='Product being purchased',
    )
    buyer_email = models.EmailField(
        help_text='Buyer email (normalized to lower case on save)',
    )
    buyer_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='store_purchases',
        help_text='Logged-in buyer, if any',
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Amount actually charged (snapshot at completion)',
    )
    currency = models.CharField(
        max_length=3,
        default='USD',
        help_text='ISO 4217 currency code',
    )
    # Stripe (same shape as CommunityMemberSubscription; webhook + payout logic lives in PaymentTransaction)
    stripe_payment_intent_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text='Stripe PaymentIntent id for this checkout',
    )
    stripe_checkout_session_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text='Stripe Checkout Session id, if the product is sold via Checkout',
    )
    stripe_customer_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text='Stripe Customer id for the buyer (optional; useful for logged-in or returning buyers)',
    )
    # Buyer billing snapshot & Paystack (parallel to Stripe checkout fields above)
    billing_country = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        help_text='ISO 3166-1 alpha-2 country for this checkout',
    )
    payment_gateway = models.CharField(
        max_length=20,
        choices=PaymentGateway.choices,
        blank=True,
        null=True,
        help_text='Payment processor handling this purchase',
    )
    paystack_customer_code = models.CharField(max_length=255, blank=True, null=True)
    paystack_subscription_code = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Set when purchase uses a Paystack subscription; usually null for one-off store sales',
    )
    paystack_transaction_reference = models.CharField(max_length=255, blank=True, null=True)
    purchased_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When payment succeeded',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StorePurchase'
        verbose_name = 'Store Purchase'
        verbose_name_plural = 'Store Purchases'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'buyer_email']),
            models.Index(fields=['status']),
            models.Index(fields=['stripe_payment_intent_id']),
            models.Index(fields=['stripe_checkout_session_id']),
            models.Index(fields=['paystack_transaction_reference']),
            models.Index(fields=['payment_gateway']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'buyer_email'],
                condition=models.Q(status='completed'),
                name='storepurchase_unique_completed_email_per_product',
            ),
        ]

    def save(self, *args, **kwargs):
        if self.buyer_email:
            self.buyer_email = self.buyer_email.strip().lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.buyer_email} – {self.product.name} ({self.status})"


class StoreDownloadToken(models.Model):
    """
    Time-limited token embedded in download links emailed after purchase or when a returning
    buyer requests a new link. Expired tokens should send the user back to the product page
    to re-enter email and issue a new token if a completed purchase exists.
    """
    purchase = models.ForeignKey(
        StorePurchase,
        on_delete=models.CASCADE,
        related_name='download_tokens',
        help_text='Purchase this download link is tied to',
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    expires_at = models.DateTimeField(help_text='When the download link stops working')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'StoreDownloadToken'
        verbose_name = 'Store Download Token'
        verbose_name_plural = 'Store Download Tokens'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"{self.token} (expires {self.expires_at})"


@receiver(post_save, sender=Community)
def _create_community_store(sender, instance, created, **kwargs):
    if created:
        CommunityStore.objects.get_or_create(community=instance)
