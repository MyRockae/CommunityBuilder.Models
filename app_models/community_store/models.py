import uuid
from decimal import Decimal

import django
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
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


class StoreProductKind(models.TextChoices):
    FILE = 'file', 'File download'
    LINK = 'link', 'External link'
    MEETING = 'meeting', 'Bookable meeting'


class StoreProduct(models.Model):
    """A digital product listed in a community store (file, external link, or bookable meeting)."""

    store = models.ForeignKey(
        CommunityStore,
        on_delete=models.CASCADE,
        related_name='products',
        help_text='Store this product belongs to',
    )
    name = models.CharField(max_length=255, help_text='Display name of the digital product')
    description = models.TextField(
        blank=True,
        null=True,
        help_text='Selling points / what the product is about',
    )
    product_kind = models.CharField(
        max_length=20,
        choices=StoreProductKind.choices,
        default=StoreProductKind.FILE,
        db_index=True,
        help_text='How the product is delivered after purchase',
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Legacy list price; prefer StoreProductPrice rows per currency',
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
    file_url = models.URLField(
        blank=True,
        null=True,
        help_text='URL of the downloadable file (required when product_kind is file)',
    )
    external_url = models.URLField(
        blank=True,
        null=True,
        help_text='Customer-facing URL when product_kind is link',
    )
    template_meeting = models.ForeignKey(
        'community_meetings.Meeting',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='store_products_ticket',
        help_text='Legacy/admin: fixed meeting row; bookable products use bookable_meeting_settings',
    )
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
            models.Index(fields=['store', 'product_kind']),
        ]

    def clean(self):
        kind = self.product_kind or StoreProductKind.FILE
        if kind == StoreProductKind.FILE:
            if not (self.file_url or '').strip():
                raise ValidationError({'file_url': 'File products require a file URL.'})
        elif kind == StoreProductKind.LINK:
            if not (self.external_url or '').strip():
                raise ValidationError({'external_url': 'Link products require an external URL.'})
        elif kind == StoreProductKind.MEETING:
            pass

    def __str__(self):
        return self.name


class StoreProductPrice(models.Model):
    """List price for a store product in one ISO 4217 currency (mirrors CommunityGroupPrice)."""

    store_product = models.ForeignKey(
        StoreProduct,
        on_delete=models.CASCADE,
        related_name='prices',
        help_text='Product this price applies to',
    )
    currency = models.CharField(
        max_length=3,
        help_text='ISO 4217 code (e.g. USD, NGN, GBP)',
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='List price in major units of this currency',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StoreProductPrice'
        verbose_name = 'Store product price'
        verbose_name_plural = 'Store product prices'
        constraints = [
            models.UniqueConstraint(
                fields=['store_product', 'currency'],
                name='storeproductprice_unique_product_currency',
            ),
        ]
        indexes = [
            models.Index(fields=['store_product', 'currency']),
        ]

    def __str__(self):
        return f'{self.store_product_id} {self.currency} {self.amount}'


class StoreBookableMeetingSettings(models.Model):
    """1:1 with a meeting-type StoreProduct: duration, buffers, and owner timezone for slot generation."""

    store_product = models.OneToOneField(
        StoreProduct,
        on_delete=models.CASCADE,
        related_name='bookable_meeting_settings',
        help_text='Meeting product these settings belong to',
    )
    time_zone = models.CharField(
        max_length=64,
        default='UTC',
        help_text='IANA timezone for interpreting weekly availability windows',
    )
    duration_minutes = models.PositiveIntegerField(
        default=30,
        validators=[MinValueValidator(1)],
        help_text='Length of each bookable slot',
    )
    buffer_before_minutes = models.PositiveIntegerField(
        default=0,
        help_text='Unbookable gap before each slot',
    )
    buffer_after_minutes = models.PositiveIntegerField(
        default=0,
        help_text='Unbookable gap after each slot',
    )
    minimum_notice_minutes = models.PositiveIntegerField(
        default=120,
        help_text='Do not offer slots starting sooner than this many minutes from now',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StoreBookableMeetingSettings'
        verbose_name = 'Store bookable meeting settings'
        verbose_name_plural = 'Store bookable meeting settings'

    def __str__(self):
        return f'Bookable settings for {self.store_product_id}'


def _store_avail_window_weekday_check_constraint():
    """Django < 5.2 uses CheckConstraint(check=...); 5.2+ uses condition= (required in Django 6+)."""
    q = models.Q(weekday__gte=1) & models.Q(weekday__lte=7)
    name = 'store_avail_window_weekday_1_7'
    if django.VERSION >= (5, 2):
        return models.CheckConstraint(condition=q, name=name)
    return models.CheckConstraint(check=q, name=name)


class StoreOwnerAvailabilityWindow(models.Model):
    """One weekly window (local times in the parent settings time_zone) for bookable meeting products."""

    settings = models.ForeignKey(
        StoreBookableMeetingSettings,
        on_delete=models.CASCADE,
        related_name='windows',
        help_text='Bookable settings this window belongs to',
    )
    weekday = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(7)],
        help_text='ISO weekday 1=Monday … 7=Sunday',
    )
    local_start = models.TimeField(help_text='Start of availability in settings.time_zone')
    local_end = models.TimeField(help_text='End of availability in settings.time_zone')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StoreOwnerAvailabilityWindow'
        verbose_name = 'Store owner availability window'
        verbose_name_plural = 'Store owner availability windows'
        constraints = [
            _store_avail_window_weekday_check_constraint(),
        ]
        indexes = [
            models.Index(fields=['settings', 'weekday']),
        ]

    def __str__(self):
        return f'{self.settings_id} weekday={self.weekday} {self.local_start}-{self.local_end}'


class StoreProductSlotHoldStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    CONVERTED = 'converted', 'Converted to purchase'
    RELEASED = 'released', 'Released'


class StoreProductSlotHold(models.Model):
    """
    Short-lived reservation of a slot while checkout completes.
    Unique (product, slot_start_utc) among pending holds prevents double booking.
    """

    store_product = models.ForeignKey(
        StoreProduct,
        on_delete=models.CASCADE,
        related_name='slot_holds',
        help_text='Product the slot belongs to',
    )
    slot_start_utc = models.DateTimeField(
        db_index=True,
        help_text='Slot start in UTC',
    )
    buyer_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='store_product_slot_holds',
        help_text='User who reserved the slot',
    )
    status = models.CharField(
        max_length=20,
        choices=StoreProductSlotHoldStatus.choices,
        default=StoreProductSlotHoldStatus.PENDING,
        db_index=True,
    )
    hold_until = models.DateTimeField(
        help_text='When this hold expires if checkout does not complete',
    )
    store_purchase = models.ForeignKey(
        'StorePurchase',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='slot_holds',
        help_text='Purchase row created for this checkout when applicable',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'StoreProductSlotHold'
        verbose_name = 'Store product slot hold'
        verbose_name_plural = 'Store product slot holds'
        constraints = [
            models.UniqueConstraint(
                fields=['store_product', 'slot_start_utc'],
                condition=models.Q(status=StoreProductSlotHoldStatus.PENDING),
                name='store_slothold_unique_pending_slot',
            ),
        ]
        indexes = [
            models.Index(fields=['store_product', 'status', 'hold_until']),
        ]

    def __str__(self):
        return f'Hold {self.store_product_id} {self.slot_start_utc} ({self.status})'


class StorePurchase(models.Model):
    """
    A checkout / payment record for a product and buyer email.

    Completed file/link purchases: at most one per (product, buyer_email).
    Completed meeting purchases: one per (product, buyer_email, booked_slot_start_utc) so repeat
    bookings on the same product are allowed.
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
        on_delete=models.PROTECT,
        related_name='store_purchases',
        help_text='Logged-in buyer',
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
    booked_slot_start_utc = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When product_kind is meeting: UTC start of the slot purchased (optional for MVP fixed meeting)',
    )
    booked_meeting = models.ForeignKey(
        'community_meetings.Meeting',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='store_purchases',
        help_text='Meeting created or linked after successful payment for meeting products',
    )
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
            models.Index(fields=['booked_slot_start_utc']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'buyer_email'],
                condition=models.Q(status='completed') & models.Q(booked_slot_start_utc__isnull=True),
                name='storepurchase_unique_completed_file_link',
            ),
            models.UniqueConstraint(
                fields=['product', 'buyer_email', 'booked_slot_start_utc'],
                condition=models.Q(status='completed') & models.Q(booked_slot_start_utc__isnull=False),
                name='storepurchase_unique_completed_meeting_slot',
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
