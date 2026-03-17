import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('community', '0010_community_is_active_flag_count'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CommunityReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(help_text='Report reason or description')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('community', models.ForeignKey(help_text='Community that was reported', on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='community.community')),
                ('user', models.ForeignKey(help_text='User who reported the community', on_delete=django.db.models.deletion.CASCADE, related_name='community_reports', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Community Report',
                'verbose_name_plural': 'Community Reports',
                'db_table': 'CommunityReport',
                'ordering': ['-created_at'],
            },
        ),
    ]
