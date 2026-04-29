from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from app_models.account.models import User
from app_models.app_payments.models import PaymentGateway
from app_models.community.models import Community


class CommunityEventVenueType(models.TextChoices):
    REMOTE = "remote", "Remote"
    PHYSICAL = "physical", "Physical"


class CommunityEvent(models.Model):
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name="events",
        help_text="Community that owns this event",
    )
    title = models.CharField(max_length=255, help_text="Event title")
    description = models.TextField(blank=True, null=True, help_text="Event description")
    starts_at = models.DateTimeField(help_text="Event start datetime")
    ends_at = models.DateTimeField(help_text="Event end datetime")
    venue_type = models.CharField(
        max_length=20,
        choices=CommunityEventVenueType.choices,
        default=CommunityEventVenueType.REMOTE,
    )
    remote_join_url = models.URLField(blank=True, null=True, help_text="Remote meeting URL")

    # Physical venue (required when venue_type=physical)
    address_line_1 = models.CharField(max_length=255, blank=True, null=True)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=120, blank=True, null=True)
    state_region = models.CharField(max_length=120, blank=True, null=True)
    postal_code = models.CharField(max_length=32, blank=True, null=True)
    country_code = models.CharField(max_length=2, blank=True, null=True)

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Legacy list price; prefer CommunityEventPrice rows per currency",
    )
    banner_url = models.URLField(blank=True, null=True, help_text="Optional event banner")
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_community_events",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "CommunityEvent"
        verbose_name = "Community event"
        verbose_name_plural = "Community events"
        ordering = ["-starts_at", "-created_at"]
        indexes = [
            models.Index(fields=["community", "starts_at"]),
            models.Index(fields=["community", "is_active"]),
        ]

    def clean(self):
        if self.ends_at and self.starts_at and self.ends_at <= self.starts_at:
            raise ValidationError({"ends_at": "End datetime must be after start datetime."})

        if self.venue_type == CommunityEventVenueType.PHYSICAL:
            required_fields = {
                "address_line_1": self.address_line_1,
                "city": self.city,
                "state_region": self.state_region,
                "postal_code": self.postal_code,
                "country_code": self.country_code,
            }
            missing = [key for key, value in required_fields.items() if not (value or "").strip()]
            if missing:
                raise ValidationError({field: "This field is required for physical events." for field in missing})
            if (self.remote_join_url or "").strip():
                raise ValidationError({"remote_join_url": "Remote URL must be empty for physical events."})

        if self.venue_type == CommunityEventVenueType.REMOTE:
            if not (self.remote_join_url or "").strip():
                raise ValidationError({"remote_join_url": "Remote URL is required for remote events."})
            for field in ("address_line_1", "address_line_2", "city", "state_region", "postal_code", "country_code"):
                if (getattr(self, field, None) or "").strip():
                    raise ValidationError({field: "Address fields must be empty for remote events."})

    def __str__(self):
        return f"{self.title} ({self.community_id})"


class CommunityEventPrice(models.Model):
    community_event = models.ForeignKey(
        CommunityEvent,
        on_delete=models.CASCADE,
        related_name="prices",
    )
    currency = models.CharField(max_length=3, help_text="ISO 4217 code (e.g. USD, NGN)")
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "CommunityEventPrice"
        verbose_name = "Community event price"
        verbose_name_plural = "Community event prices"
        constraints = [
            models.UniqueConstraint(
                fields=["community_event", "currency"],
                name="communityeventprice_unique_event_currency",
            )
        ]
        indexes = [models.Index(fields=["community_event", "currency"])]


class EventRegistration(models.Model):
    STATUS_PENDING = "pending"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"
    STATUS_REFUNDED = "refunded"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending payment"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_FAILED, "Failed"),
        (STATUS_REFUNDED, "Refunded"),
    ]

    event = models.ForeignKey(
        CommunityEvent,
        on_delete=models.CASCADE,
        related_name="registrations",
        help_text="Event being registered for",
    )
    attendee_user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="event_registrations",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default="USD")

    stripe_payment_intent_id = models.CharField(max_length=255, null=True, blank=True)
    stripe_checkout_session_id = models.CharField(max_length=255, null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)

    billing_country = models.CharField(max_length=2, blank=True, null=True)
    payment_gateway = models.CharField(
        max_length=20,
        choices=PaymentGateway.choices,
        blank=True,
        null=True,
    )
    paystack_customer_code = models.CharField(max_length=255, blank=True, null=True)
    paystack_transaction_reference = models.CharField(max_length=255, blank=True, null=True)

    purchased_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "EventRegistration"
        verbose_name = "Event registration"
        verbose_name_plural = "Event registrations"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["event", "status"]),
            models.Index(fields=["attendee_user", "status"]),
            models.Index(fields=["stripe_payment_intent_id"]),
            models.Index(fields=["paystack_transaction_reference"]),
            models.Index(fields=["payment_gateway"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["event", "attendee_user"],
                condition=models.Q(status="completed"),
                name="eventregistration_unique_completed_attendee_per_event",
            )
        ]

    def __str__(self):
        return f"{self.event_id}:{self.attendee_user_id} ({self.status})"
