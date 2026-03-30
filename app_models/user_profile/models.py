from django.db import models
from app_models.account.models import User
from app_models.shared.models import Tag

def user_directory_path(instance, filename):
    # Extract the file extension (if any)
    ext = filename.split('.')[-1] if '.' in filename else ''
    # Create the new filename using the user's id
    new_filename = f"{instance.user.id}.{ext}" if ext else f"{instance.user.id}"
    # Save the file inside the public_html folder
    return f'rockae_user_profile/{new_filename}'

class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True, help_text='User date of birth')
    country = models.CharField(max_length=100, null=True, blank=True, help_text='User country name')
    country_flag_url = models.URLField(blank=True, null=True, help_text='URL of the country flag')
    thumbnail_url = models.URLField(blank=True, null=True)
    bio = models.TextField(null=True, blank=True)
    about = models.TextField(null=True, blank=True, help_text='Detailed information about the user')
    interest = models.ManyToManyField(Tag, related_name='user_profiles', blank=True)

    def __str__(self):
        return self.last_name

    class Meta:
        db_table = 'UserProfile'
        verbose_name = 'UserProfile'
        verbose_name_plural = 'UserProfile'


class UserAddress(models.Model):
    """
    Postal-style address lines for display. Use billing_country / billing_region for
    tax and payment-provider routing; state is reserved for other product use.
    At most one row per user should have is_default_billing=True (PostgreSQL UniqueConstraint).
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='addresses',
        help_text='Owner of this address',
    )
    street_line1 = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text='Street address, line 1',
    )
    street_line2 = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Street address, line 2 (optional)',
    )
    city = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Country name for display (e.g. on invoices)',
    )
    billing_country = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        help_text='ISO 3166-1 alpha-2; set for billing addresses for Paystack/Stripe routing',
    )
    billing_region = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='State/province or subdivision for tax and payment routing (e.g. code or name as required by the gateway)',
    )
    state = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Optional app-specific use (not the same as billing_region unless you choose to mirror it)',
    )
    is_billing_address = models.BooleanField(
        default=False,
        help_text='True if this address is used for billing/invoicing',
    )
    is_default_billing = models.BooleanField(
        default=False,
        help_text='True if this is the default billing address among billing rows',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'UserAddress'
        verbose_name = 'User address'
        verbose_name_plural = 'User addresses'
        ordering = ['-is_default_billing', '-updated_at']
        indexes = [
            models.Index(fields=['user', 'is_billing_address']),
            models.Index(fields=['user', 'is_default_billing']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                condition=models.Q(is_default_billing=True),
                name='useraddress_unique_default_billing_per_user',
            ),
        ]

    def __str__(self):
        parts = [
            self.street_line1,
            self.city,
            self.billing_region,
            self.country or self.billing_country,
        ]
        return ', '.join(p for p in parts if p) or f'Address #{self.pk}'
