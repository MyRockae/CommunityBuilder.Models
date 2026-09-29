from django.db import migrations, models
from django.db.models import F


def backfill_published_posts(apps, schema_editor):
    CommunityBlogPost = apps.get_model('community_blog', 'CommunityBlogPost')
    CommunityBlogPost.objects.filter(is_published=True, published_at__isnull=True).update(
        published_at=F('created_at'),
    )


class Migration(migrations.Migration):

    dependencies = [
        ('community_blog', '0002_communityblogpost_is_published'),
    ]

    operations = [
        migrations.AddField(
            model_name='communityblogpost',
            name='published_at',
            field=models.DateTimeField(
                blank=True,
                help_text='Set once when the post is first published; remains set if is_published is toggled off so downstream notifications fire only once.',
                null=True,
            ),
        ),
        migrations.RunPython(backfill_published_posts, migrations.RunPython.noop),
    ]
