from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0007_communityview'),
    ]

    operations = [
        migrations.AddField(
            model_name='communityview',
            name='referrer_url',
            field=models.URLField(blank=True, help_text='URL of the referring page', max_length=2048, null=True),
        ),
        migrations.AddField(
            model_name='communityview',
            name='referrer_domain',
            field=models.CharField(blank=True, help_text='Domain of the referrer', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='communityview',
            name='country',
            field=models.CharField(blank=True, help_text='Country of the viewer', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='communityview',
            name='region',
            field=models.CharField(blank=True, help_text='Region/state of the viewer', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='communityview',
            name='city',
            field=models.CharField(blank=True, help_text='City of the viewer', max_length=100, null=True),
        ),
    ]
