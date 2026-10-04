from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community_store', '0013_rename_storegueste_email_ex_idx_storegueste_email_d45c55_idx_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storeslotsession',
            name='host_start_url',
            field=models.URLField(blank=True, default='', max_length=2048),
        ),
        migrations.AlterField(
            model_name='storeslotsession',
            name='join_url',
            field=models.URLField(blank=True, default='', max_length=2048),
        ),
    ]
