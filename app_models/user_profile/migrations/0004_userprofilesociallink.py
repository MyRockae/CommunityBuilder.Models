import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0003_rename_useraddress_user_bill_idx_useraddress_user_id_9fdbb6_idx_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfileSocialLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('platform', models.CharField(help_text='Platform key for display/icons (e.g. website, twitter, discord, linkedin)', max_length=64)),
                ('url', models.URLField(help_text='Full URL for this link', max_length=2048)),
                ('sort_order', models.PositiveSmallIntegerField(default=0, help_text='Lower values appear first when listing links')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user_profile', models.ForeignKey(help_text='User profile this link belongs to', on_delete=django.db.models.deletion.CASCADE, related_name='social_links', to='user_profile.userprofile')),
            ],
            options={
                'verbose_name': 'User profile social link',
                'verbose_name_plural': 'User profile social links',
                'db_table': 'UserProfileSocialLink',
                'ordering': ['sort_order', 'id'],
            },
        ),
    ]
