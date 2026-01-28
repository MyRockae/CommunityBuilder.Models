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
