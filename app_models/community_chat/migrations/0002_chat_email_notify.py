from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community_chat', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversationparticipant',
            name='email_notify_after',
            field=models.DateTimeField(
                blank=True,
                help_text='When a delayed unread-chat email may send; cleared on read or after send',
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='conversationparticipant',
            name='last_chat_email_at',
            field=models.DateTimeField(
                blank=True,
                help_text='When the last unread-chat email was sent for this thread',
                null=True,
            ),
        ),
        migrations.AddIndex(
            model_name='conversationparticipant',
            index=models.Index(
                condition=models.Q(('email_notify_after__isnull', False)),
                fields=['email_notify_after'],
                name='chat_part_email_notify_idx',
            ),
        ),
    ]
