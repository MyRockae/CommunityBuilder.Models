from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0026_communitygroup_trial_days'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeaturedCommunity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('featured_image_url', models.URLField()),
                ('display_order', models.PositiveIntegerField(db_index=True, default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                (
                    'community',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='featured_slot',
                        to='community.community',
                    ),
                ),
            ],
            options={
                'db_table': 'FeaturedCommunity',
                'ordering': ['display_order', 'id'],
            },
        ),
    ]
