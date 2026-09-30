from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0030_community_bunny_collection_id'),
        ('community_course', '0013_coursebundle_is_published_published_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursebundle',
            name='community_groups',
            field=models.ManyToManyField(
                blank=True,
                help_text='Community groups (tiers) that have access to this classroom',
                related_name='course_bundles',
                to='community.communitygroup',
            ),
        ),
    ]
