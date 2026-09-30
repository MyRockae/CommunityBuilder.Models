from django.db import migrations, models


def backfill_image_ref(apps, schema_editor):
    Inbox = apps.get_model('bulk_notification', 'UserInboxNotification')

    def copy_banners(event_type, model_label, field_name):
        app_label, model_name = model_label.split('.')
        try:
            Entity = apps.get_model(app_label, model_name)
        except LookupError:
            return
        banners = {
            pk: (ref or '')
            for pk, ref in Entity.objects.exclude(**{f'{field_name}': ''})
            .exclude(**{f'{field_name}__isnull': True})
            .values_list('pk', field_name)
        }
        if not banners:
            return
        rows = Inbox.objects.filter(event_type=event_type, image_ref='')
        updates = []
        for row in rows.iterator():
            ref = banners.get(row.object_id)
            if not ref:
                continue
            row.image_ref = ref[:1024]
            updates.append(row)
            if len(updates) >= 500:
                Inbox.objects.bulk_update(updates, ['image_ref'])
                updates = []
        if updates:
            Inbox.objects.bulk_update(updates, ['image_ref'])

    copy_banners('course_published', 'community_course.Course', 'banner_url')
    copy_banners('classroom_created', 'community_course.CourseBundle', 'banner_url')
    copy_banners('blog_post', 'community_blog.CommunityBlogPost', 'image_url')
    copy_banners('roadmap_published', 'learning_journey.LearningJourney', 'banner_url')
    copy_banners('roadmap_updated', 'learning_journey.LearningJourney', 'banner_url')


class Migration(migrations.Migration):

    dependencies = [
        ('bulk_notification', '0009_group_access_events'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinboxnotification',
            name='image_ref',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Entity banner or cover for content bells; staff photo stays on actor_avatar_ref',
                max_length=1024,
            ),
        ),
        migrations.RunPython(backfill_image_ref, migrations.RunPython.noop),
    ]
