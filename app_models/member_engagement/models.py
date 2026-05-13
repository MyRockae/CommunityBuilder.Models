import uuid

from django.db import models

from app_models.account.models import User
from app_models.community.models import Community
from app_models.community_classroom.models import Classroom


class EngagementSession(models.Model):
    """Logical client session for batched engagement telemetry (per tab / client_session_key)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='engagement_sessions')
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name='engagement_sessions',
    )
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='engagement_sessions',
        help_text='Classroom context when tracking classroom surfaces; null for community-only events.',
    )
    client_session_key = models.CharField(
        max_length=64,
        help_text='Opaque client-generated session id (per tab).',
    )
    started_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(auto_now=True)
    user_agent = models.CharField(max_length=512, blank=True, null=True)

    class Meta:
        db_table = 'EngagementSession'
        verbose_name = 'Engagement session'
        verbose_name_plural = 'Engagement sessions'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'community', 'client_session_key'],
                name='uniq_engagementsession_user_community_clientkey',
            ),
        ]
        indexes = [
            models.Index(fields=['community', 'classroom', '-last_seen_at'], name='engsess_comm_cl_last_idx'),
            models.Index(fields=['user', '-last_seen_at'], name='engsess_user_last_idx'),
        ]

    def __str__(self):
        return f'EngagementSession {self.id} user={self.user_id}'


class EngagementEvent(models.Model):
    """Append-only engagement event row (retries use idempotency_key)."""

    class Surface(models.TextChoices):
        CLASSROOM_HOME = 'classroom_home', 'Classroom home'
        LESSON = 'lesson', 'Lesson'
        CONTENT = 'content', 'Content'
        MATERIAL = 'material', 'Material'
        VIDEO = 'video', 'Video'

    session = models.ForeignKey(
        EngagementSession,
        on_delete=models.CASCADE,
        related_name='events',
    )
    occurred_at_client = models.DateTimeField(null=True, blank=True)
    received_at = models.DateTimeField(auto_now_add=True)
    surface = models.CharField(max_length=32, choices=Surface.choices)
    resource_type = models.CharField(max_length=64, blank=True, null=True)
    resource_id = models.CharField(max_length=64, blank=True, null=True)
    event_type = models.CharField(max_length=32)
    duration_ms = models.PositiveIntegerField(null=True, blank=True)
    payload = models.JSONField(default=dict, blank=True)
    idempotency_key = models.CharField(max_length=128, unique=True)

    class Meta:
        db_table = 'EngagementEvent'
        verbose_name = 'Engagement event'
        verbose_name_plural = 'Engagement events'
        indexes = [
            models.Index(fields=['session', 'received_at'], name='engevent_sess_recv_idx'),
        ]

    def __str__(self):
        return f'EngagementEvent {self.pk} {self.event_type}'
