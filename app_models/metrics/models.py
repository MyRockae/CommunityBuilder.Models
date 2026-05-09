from django.db import models
from django.db.models import Q

from app_models.account.models import User
from app_models.community.models import Community


class UserMetricRollup(models.Model):
    """
    Narrow rollup row per (user, optional community scope, metric_key).
    Global stats use community=NULL; per-community stats set community FK.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='metric_rollups',
        help_text='User this metric applies to',
    )
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='user_metric_rollups',
        help_text='Null for platform-wide metrics; set for community-scoped metrics',
    )
    metric_key = models.CharField(
        max_length=64,
        db_index=True,
        help_text='Stable metric identifier (e.g. likes_given, likes_received)',
    )
    value = models.BigIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'UserMetricRollup'
        verbose_name = 'User metric rollup'
        verbose_name_plural = 'User metric rollups'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'metric_key'],
                condition=Q(community__isnull=True),
                name='user_metric_rollup_global_uq',
            ),
            models.UniqueConstraint(
                fields=['user', 'community', 'metric_key'],
                condition=Q(community__isnull=False),
                name='user_metric_rollup_scoped_uq',
            ),
        ]
        indexes = [
            models.Index(
                fields=['community', 'metric_key', '-value'],
                name='user_metric_rollup_leader_idx',
            ),
            models.Index(
                fields=['user', 'metric_key'],
                name='umrollup_user_key_idx',  # models.E034: index names <=30 chars
            ),
        ]

    def __str__(self):
        scope = f'community={self.community_id}' if self.community_id else 'global'
        return f'{self.user_id} {scope} {self.metric_key}={self.value}'
