import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0006_communitymember_leaderboard_year'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CommunityView',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('viewed_at', models.DateTimeField(auto_now_add=True, help_text='When the view was recorded')),
                ('community', models.ForeignKey(help_text='Community that was viewed', on_delete=django.db.models.deletion.CASCADE, related_name='community_views', to='community.community')),
                ('user', models.ForeignKey(blank=True, help_text='User who viewed; null for anonymous views.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='community_views', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Community View',
                'verbose_name_plural': 'Community Views',
                'db_table': 'CommunityView',
                'ordering': ['-viewed_at'],
            },
        ),
    ]
