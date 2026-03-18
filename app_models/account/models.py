from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
from app_models.shared.validators import slug_username_validator


class Permission(models.Model):
    """Permission that can be assigned to roles (e.g. manage_users, moderate_community)."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Permission'
        verbose_name = 'Permission'
        verbose_name_plural = 'Permissions'
        ordering = ['name']

    def __str__(self):
        return self.name


class Role(models.Model):
    """Role with optional permissions. Use is_admin_role for staff/admin vs normal users."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_admin_role = models.BooleanField(default=False, help_text='If True, treated as staff/admin for access control.')
    permissions = models.ManyToManyField(
        Permission,
        related_name='roles',
        blank=True,
        help_text='Permissions granted by this role.',
    )

    class Meta:
        db_table = 'Roles'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
        ordering = ['name']

    def __str__(self):
        return self.name


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a User with the given email and password.
        Roles are not set here; the API decides and can pass roles= or assign later.
        """
        if not email:
            raise ValueError('The Email must be set')

        extra_fields.setdefault('is_staff', False)
        roles = extra_fields.pop('roles', None)

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        if roles is not None:
            user.roles.set(roles)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        Sets is_staff=True only; the API decides which role(s) to assign.
        """
        extra_fields['is_staff'] = True
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=True,
        null=True,
        db_index=True,
        validators=[slug_username_validator],
        help_text='Only letters, numbers, hyphens (-) and underscores (_) allowed.',
    )
    password = models.CharField(max_length=128)  # Hashed password (from AbstractBaseUser)
    roles = models.ManyToManyField(
        Role,
        related_name='users',
        blank=True,
        help_text='Roles assigned to this user (replaces single role for scaling).',
    )
    is_staff = models.BooleanField(default=False, help_text='Designates staff/admin access (e.g. Django admin).')
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)  # From AbstractBaseUser
    verification_token = models.CharField(max_length=64, blank=True, null=True)
    reset_password_token = models.CharField(max_length=64, blank=True, null=True)
    token_expires_at = models.DateTimeField(blank=True, null=True)
    pending_email = models.EmailField(blank=True, null=True, help_text='New email address pending verification')
    email_change_code = models.CharField(max_length=6, blank=True, null=True, help_text='6-digit verification code for email change')
    email_change_code_expires_at = models.DateTimeField(blank=True, null=True, help_text='Expiration time for email change code')

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def generate_verification_token(self):
        self.verification_token = get_random_string(length=64)
        self.token_expires_at = timezone.now() + timezone.timedelta(hours=24)
        self.save(update_fields=['verification_token', 'token_expires_at'])

    def generate_reset_token(self):
        self.reset_password_token = get_random_string(length=64)
        self.token_expires_at = timezone.now() + timezone.timedelta(hours=1)
        self.save(update_fields=['reset_password_token', 'token_expires_at'])

    def __str__(self):
        return self.email

    class Meta:
        db_table = 'User'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
