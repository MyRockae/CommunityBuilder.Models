from django.db import migrations, models


EVENT_CHOICES = [
    ('town_hall_post', 'Town hall post'),
    ('forum_post', 'Forum post'),
    ('blog_post', 'Blog post'),
    ('course_published', 'Course published'),
    ('course_lesson_added', 'Course lesson added'),
    ('resource_activated', 'Resource content activated'),
    ('classroom_created', 'Classroom created'),
    ('classroom_course_added', 'Classroom course added'),
    ('poll_created', 'Poll created'),
    ('meeting_created', 'Meeting created'),
    ('roadmap_published', 'Roadmap published'),
    ('roadmap_updated', 'Roadmap updated'),
    ('group_access_granted', 'Group access granted'),
    ('group_access_revoked', 'Group access revoked'),
    ('join_request', 'Join request'),
    ('community_feedback', 'Community feedback'),
    ('quiz_submission', 'Quiz submission'),
    ('blog_reply', 'Blog reply'),
    ('forum_reply', 'Forum reply'),
    ('town_hall_reply', 'Town hall reply'),
    ('public_feed_reply', 'Public feed reply'),
    ('form_response', 'Form response'),
    ('inactive_user', 'Inactive user'),
    ('views_momentum', 'Community views momentum'),
    ('marketing_campaign', 'Marketing campaign'),
]


class Migration(migrations.Migration):

    dependencies = [
        ('bulk_notification', '0008_roadmap_updated_event'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificationbatch',
            name='event_type',
            field=models.CharField(
                choices=EVENT_CHOICES,
                help_text='Which notification this batch represents',
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name='notificationdelivery',
            name='event_type',
            field=models.CharField(
                choices=EVENT_CHOICES,
                help_text='Denormalised from the batch so cooldown lookups avoid a join',
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name='userinboxnotification',
            name='event_type',
            field=models.CharField(choices=EVENT_CHOICES, max_length=32),
        ),
    ]
