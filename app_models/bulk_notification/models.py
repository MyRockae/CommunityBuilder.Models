from django.db import models

from app_models.account.models import User
from app_models.community.models import Community


class NotificationEvent(models.TextChoices):
    TOWN_HALL_POST = 'town_hall_post', 'Town hall post'
    FORUM_POST = 'forum_post', 'Forum post'
    BLOG_POST = 'blog_post', 'Blog post'
    COURSE_PUBLISHED = 'course_published', 'Course published'
    COURSE_LESSON_ADDED = 'course_lesson_added', 'Course lesson added'
    RESOURCE_ACTIVATED = 'resource_activated', 'Resource content activated'
    CLASSROOM_CREATED = 'classroom_created', 'Classroom created'
    CLASSROOM_COURSE_ADDED = 'classroom_course_added', 'Classroom course added'
    POLL_CREATED = 'poll_created', 'Poll created'
    MEETING_CREATED = 'meeting_created', 'Meeting created'
    ROADMAP_PUBLISHED = 'roadmap_published', 'Roadmap published'
    ROADMAP_UPDATED = 'roadmap_updated', 'Roadmap updated'
    GROUP_ACCESS_GRANTED = 'group_access_granted', 'Group access granted'
    GROUP_ACCESS_REVOKED = 'group_access_revoked', 'Group access revoked'
    JOIN_REQUEST = 'join_request', 'Join request'
    COMMUNITY_FEEDBACK = 'community_feedback', 'Community feedback'
    QUIZ_SUBMISSION = 'quiz_submission', 'Quiz submission'
    BLOG_REPLY = 'blog_reply', 'Blog reply'
    FORUM_REPLY = 'forum_reply', 'Forum reply'
    TOWN_HALL_REPLY = 'town_hall_reply', 'Town hall reply'
    PUBLIC_FEED_REPLY = 'public_feed_reply', 'Public feed reply'
    FORM_RESPONSE = 'form_response', 'Form response'
    INACTIVE_USER = 'inactive_user', 'Inactive user'
    VIEWS_MOMENTUM = 'views_momentum', 'Community views momentum'
    MARKETING_CAMPAIGN = 'marketing_campaign', 'Marketing campaign'


class NotificationBatchStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    DISPATCHED = 'dispatched', 'Dispatched'
    SENDING = 'sending', 'Sending'
    COMPLETE = 'complete', 'Complete'
    FAILED = 'failed', 'Failed'


class NotificationBatch(models.Model):
    """
    Outbox row for one bulk notification. Written in the same transaction as the
    object that triggered it, so a notification cannot be lost if the queue is
    unreachable; a sweep re-dispatches rows left in PENDING.
    """

    event_type = models.CharField(
        max_length=32,
        choices=NotificationEvent.choices,
        help_text='Which notification this batch represents',
    )
    dedupe_key = models.CharField(
        max_length=128,
        unique=True,
        help_text='Stable key per logical notification (e.g. town_hall_post:8412); makes re-triggers no-ops',
    )
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notification_batches',
        help_text='Null for platform-wide notifications such as inactive_user',
    )
    object_id = models.BigIntegerField(
        null=True,
        blank=True,
        help_text='Primary key of the triggering object (post, blog post, course); null for platform-wide scans',
    )
    actor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='triggered_notification_batches',
        help_text='User who triggered the notification; excluded from recipients',
    )
    status = models.CharField(
        max_length=16,
        choices=NotificationBatchStatus.choices,
        default=NotificationBatchStatus.PENDING,
        db_index=True,
    )
    recipient_count = models.IntegerField(default=0)
    sent_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    last_error = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'NotificationBatch'
        verbose_name = 'Notification batch'
        verbose_name_plural = 'Notification batches'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at'], name='notif_batch_status_idx'),
            models.Index(fields=['event_type', 'created_at'], name='notif_batch_event_idx'),
        ]

    def __str__(self):
        return f'{self.dedupe_key} ({self.status})'


class NotificationDelivery(models.Model):
    """
    One row per recipient per batch. Answers "did this member get it", suppresses
    duplicate sends on retry, and backs the resend cooldown for recurring scans.
    """

    batch = models.ForeignKey(
        NotificationBatch,
        on_delete=models.CASCADE,
        related_name='deliveries',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notification_deliveries',
    )
    email = models.EmailField()
    event_type = models.CharField(
        max_length=32,
        choices=NotificationEvent.choices,
        help_text='Denormalised from the batch so cooldown lookups avoid a join',
    )
    sent_at = models.DateTimeField(null=True, blank=True)
    error = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'NotificationDelivery'
        verbose_name = 'Notification delivery'
        verbose_name_plural = 'Notification deliveries'
        constraints = [
            models.UniqueConstraint(
                fields=['batch', 'user'],
                name='notif_delivery_batch_user_uq',
            ),
        ]
        indexes = [
            models.Index(fields=['user', 'event_type', '-sent_at'], name='notif_deliv_cooldown_idx'),
        ]

    def __str__(self):
        return f'{self.email} <- batch {self.batch_id}'


class MemberNotificationPreference(models.Model):
    """
    Opt-out only. Absence of a row means the member receives everything, so
    existing members are not silently unsubscribed when this ships.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notification_preferences',
    )
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name='member_notification_preferences',
    )
    muted_events = models.JSONField(
        default=list,
        blank=True,
        help_text='Event ids this member has opted out of (e.g. ["town_hall_post"])',
    )
    unsubscribed_all = models.BooleanField(
        default=False,
        help_text='When true, no bulk notifications are sent for this community',
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'MemberNotificationPreference'
        verbose_name = 'Member notification preference'
        verbose_name_plural = 'Member notification preferences'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'community'],
                name='member_notif_pref_uq',
            ),
        ]

    def __str__(self):
        return f'prefs user={self.user_id} community={self.community_id}'


class PlatformNotificationPreference(models.Model):
    """
    Account-level opt-out for platform mail that belongs to no community.

    Kept apart from ``MemberNotificationPreference``, which is scoped to a community and
    so cannot record an opt-out for a user who has joined none, and apart from
    ``EmailSuppression``, which is a reputation block for addresses we must never touch
    again. Opting out of marketing must not stop community notifications or password
    resets.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='platform_notification_preference',
    )
    marketing_opt_out = models.BooleanField(
        default=False,
        help_text='When true, the user receives no marketing campaigns',
    )
    inactive_user_opt_out = models.BooleanField(
        default=False,
        help_text='When true, the user receives no re-engagement reminders',
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'PlatformNotificationPreference'
        verbose_name = 'Platform notification preference'
        verbose_name_plural = 'Platform notification preferences'

    def __str__(self):
        return f'platform prefs user={self.user_id}'


class EmailCampaignStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    SENDING = 'sending', 'Sending'
    SENT = 'sent', 'Sent'
    FAILED = 'failed', 'Failed'


class EmailCampaignAudience(models.TextChoices):
    ALL_USERS = 'all_users', 'All verified active users'


class EmailCampaign(models.Model):
    """
    An admin-authored marketing email.

    The body is stored as an editor document rather than HTML so the send path can
    render email-safe markup itself; accepting HTML from a browser would mean shipping
    whatever the editor emitted straight to an inbox.

    Progress is not duplicated here. Once ``batch`` is set, counts and terminal state
    come from that row, so there is one writer for delivery state.
    """

    title = models.CharField(
        max_length=255,
        help_text='Internal name, never shown to recipients',
    )
    subject = models.CharField(max_length=255)
    preheader = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text='Preview text shown after the subject in most inboxes',
    )
    content_json = models.JSONField(
        default=dict,
        blank=True,
        help_text='Editor document; rendered to email-safe HTML at send time',
    )
    hero_image_url = models.CharField(
        max_length=1024,
        blank=True,
        default='',
        help_text='Storage ref for the banner image; must live under the public/ zone',
    )
    attachments = models.JSONField(
        default=list,
        blank=True,
        help_text=(
            'Downloadable files sent with the campaign. Each item is '
            '{storage_ref, filename, content_type, size_bytes} under the public/ zone.'
        ),
    )
    audience = models.CharField(
        max_length=32,
        choices=EmailCampaignAudience.choices,
        default=EmailCampaignAudience.ALL_USERS,
    )
    status = models.CharField(
        max_length=16,
        choices=EmailCampaignStatus.choices,
        default=EmailCampaignStatus.DRAFT,
        db_index=True,
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='email_campaigns',
    )
    batch = models.ForeignKey(
        NotificationBatch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='email_campaigns',
        help_text='Set when the campaign is sent; source of truth for delivery counts',
    )
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'EmailCampaign'
        verbose_name = 'Email campaign'
        verbose_name_plural = 'Email campaigns'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at'], name='email_campaign_status_idx'),
        ]

    def __str__(self):
        return f'{self.title} ({self.status})'


class EmailSuppression(models.Model):
    """
    Hard bounces and spam complaints. Checked on every fan-out so a bad address
    cannot keep degrading sender reputation for the whole platform.
    """

    REASON_CHOICES = [
        ('hard_bounce', 'Hard bounce'),
        ('spam_complaint', 'Spam complaint'),
        ('invalid', 'Invalid address'),
        ('manual', 'Manually suppressed'),
    ]

    email = models.EmailField(unique=True)
    reason = models.CharField(max_length=32, choices=REASON_CHOICES, default='hard_bounce')
    detail = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'EmailSuppression'
        verbose_name = 'Email suppression'
        verbose_name_plural = 'Email suppressions'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.email} ({self.reason})'


class UserInboxNotification(models.Model):
    """
    Per-recipient in-app inbox row. Independent of email/Telegram delivery.
    Dismissing or reading only affects this user.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='inbox_notifications',
    )
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name='inbox_notifications',
    )
    actor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='triggered_inbox_notifications',
    )
    batch = models.ForeignKey(
        NotificationBatch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inbox_notifications',
    )
    event_type = models.CharField(max_length=32, choices=NotificationEvent.choices)
    object_id = models.BigIntegerField()
    object_type = models.CharField(max_length=32, blank=True, default='')
    actor_name = models.CharField(max_length=255, blank=True, default='')
    actor_avatar_ref = models.CharField(max_length=1024, blank=True, default='')
    title = models.CharField(max_length=255, blank=True, default='')
    excerpt = models.TextField(blank=True, default='')
    deep_link = models.CharField(max_length=512, blank=True, default='')
    read_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'UserInboxNotification'
        verbose_name = 'User inbox notification'
        verbose_name_plural = 'User inbox notifications'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'community', 'event_type', 'object_id'],
                name='inbox_notif_user_event_obj_uq',
            ),
        ]
        indexes = [
            models.Index(
                fields=['user', 'community', 'deleted_at', '-created_at'],
                name='inbox_notif_list_idx',
            ),
            models.Index(
                fields=['user', 'community', 'read_at'],
                name='inbox_notif_unread_idx',
            ),
        ]

    def __str__(self):
        return f'{self.event_type} -> user={self.user_id} community={self.community_id}'
