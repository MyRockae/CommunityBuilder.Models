import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0017_communitygroup_billing_period_flags'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommunitySocialLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('platform', models.CharField(help_text='Platform key for display/icons (e.g. website, twitter, discord, linkedin)', max_length=64)),
                ('url', models.URLField(help_text='Full URL for this link', max_length=2048)),
                ('sort_order', models.PositiveSmallIntegerField(default=0, help_text='Lower values appear first when listing links')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('community', models.ForeignKey(help_text='Community this link belongs to', on_delete=django.db.models.deletion.CASCADE, related_name='social_links', to='community.community')),
            ],
            options={
                'verbose_name': 'Community social link',
                'verbose_name_plural': 'Community social links',
                'db_table': 'CommunitySocialLink',
                'ordering': ['sort_order', 'id'],
            },
        ),
    ]
