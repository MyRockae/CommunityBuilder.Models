from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('community_resource', '0012_resourcecontent_activated_at'),
        ('community', '0033_remove_companion_request_pref_help'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CommunityDriveConnection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_email', models.EmailField(blank=True, default='', max_length=254)),
                ('provider_user_id', models.CharField(blank=True, default='', max_length=255)),
                ('refresh_token_encrypted', models.TextField(blank=True, default='')),
                ('access_token_encrypted', models.TextField(blank=True, default='')),
                ('access_token_expires_at', models.DateTimeField(blank=True, null=True)),
                ('scopes', models.TextField(blank=True, default='')),
                ('status', models.CharField(
                    choices=[('active', 'Active'), ('expired', 'Expired'), ('revoked', 'Revoked')],
                    db_index=True,
                    default='active',
                    max_length=20,
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('community', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='drive_connection',
                    to='community.community',
                )),
                ('connected_by', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='community_drive_connections',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'verbose_name': 'Community Drive connection',
                'verbose_name_plural': 'Community Drive connections',
                'db_table': 'CommunityDriveConnection',
            },
        ),
        migrations.AddField(
            model_name='resourcecontent',
            name='drive_file_id',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Google Drive file id when content_source is google_drive',
                max_length=128,
            ),
        ),
        migrations.AddField(
            model_name='resourcecontent',
            name='drive_file_name',
            field=models.CharField(blank=True, default='', max_length=512),
        ),
        migrations.AddField(
            model_name='resourcecontent',
            name='drive_mime_type',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]
