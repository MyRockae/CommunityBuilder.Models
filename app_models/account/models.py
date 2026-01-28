from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string

class UserRole(models.Model):
    """User role model with admin and user roles"""
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
    ]
    
    name = models.CharField(max_length=20, choices=ROLE_CHOICES, unique=True)
    
    def __str__(self):
        return self.get_name_display()
    
    class Meta:
        db_table = 'UserRole'
        verbose_name = 'UserRole'
        verbose_name_plural = 'UserRoles'

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular User with the given email and password.
        If no role is provided, assigns 'user' role by default.
        """
        if not email:
            raise ValueError('The Email must be set')
        
        # Assign 'user' role by default if no role is provided
        if 'role' not in extra_fields or extra_fields.get('role') is None:
            user_role, _ = UserRole.objects.get_or_create(name='user')
            extra_fields['role'] = user_role
            
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # Hashes the password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        Admin role will be assigned.
        """
        admin_role, _ = UserRole.objects.get_or_create(name='admin')
        extra_fields['role'] = admin_role
        
        return self.create_user(email, password, **extra_fields)
            
class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True, blank=True, null=True, db_index=True)
    password = models.CharField(max_length=128)  # Hashed password (from AbstractBaseUser)
    role = models.ForeignKey(UserRole, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
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
