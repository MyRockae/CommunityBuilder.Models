import uuid

import django
from django.db import models
from django.db.models import Q, F

from app_models.account.models import User
from app_models.community.models import Community, CommunityMember
from app_models.community_course.models import Course, CourseBundle


def _edge_no_self_loop_constraint():
    """
    Django 5+ uses CheckConstraint(condition=...); Django 4.x uses check=...
    (Django 6 dropped `check`.)
    """
    q = ~Q(from_node=F('to_node'))
    if django.VERSION >= (5, 0):
        return models.CheckConstraint(condition=q, name='learning_journey_edge_no_self_loop')
    return models.CheckConstraint(check=q, name='learning_journey_edge_no_self_loop')


def _node_target_xor_constraint():
    """Exactly one of course_bundle or course must be set."""
    q = (
        Q(course_bundle__isnull=False, course__isnull=True)
        | Q(course_bundle__isnull=True, course__isnull=False)
    )
    if django.VERSION >= (5, 0):
        return models.CheckConstraint(condition=q, name='learning_journey_node_target_xor')
    return models.CheckConstraint(check=q, name='learning_journey_node_target_xor')


class LearningJourney(models.Model):
    """Community-defined directed graph of course bundles for guided paths."""

    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name='learning_journeys',
        help_text='Community this journey belongs to',
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    banner_url = models.URLField(blank=True, null=True)
    is_published = models.BooleanField(default=False, help_text='Visible to members when True')
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='learning_journeys_created',
        help_text='Owner/co-owner who created the journey',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'LearningJourney'
        verbose_name = 'Learning Journey'
        verbose_name_plural = 'Learning Journeys'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['community']),
            models.Index(fields=['community', 'is_published']),
        ]

    def __str__(self):
        return f'{self.title} ({self.community_id})'


class LearningJourneyNode(models.Model):
    """One journey stage: either a course bundle or a single course."""

    journey = models.ForeignKey(
        LearningJourney,
        on_delete=models.CASCADE,
        related_name='nodes',
    )
    course_bundle = models.ForeignKey(
        CourseBundle,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='learning_journey_nodes',
        help_text='Course bundle for this stage (mutually exclusive with course)',
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='learning_journey_nodes',
        help_text='Single course for this stage (mutually exclusive with course_bundle)',
    )
    offerings = models.JSONField(
        default=dict,
        blank=True,
        help_text='Owner-defined perks/copy for this stage (e.g. bullets, headline)',
    )
    stable_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        help_text='Stable identity for API graph replace operations',
    )
    layout_x = models.FloatField(
        null=True,
        blank=True,
        help_text='Editor/preview canvas X (React Flow space); null = use auto-layout',
    )
    layout_y = models.FloatField(
        null=True,
        blank=True,
        help_text='Editor/preview canvas Y (React Flow space); null = use auto-layout',
    )

    class Meta:
        db_table = 'LearningJourneyNode'
        verbose_name = 'Learning Journey Node'
        verbose_name_plural = 'Learning Journey Nodes'
        constraints = [
            _node_target_xor_constraint(),
            models.UniqueConstraint(
                fields=['journey', 'course_bundle'],
                condition=Q(course_bundle__isnull=False),
                name='uniq_ljnode_journey_bundle',
            ),
            models.UniqueConstraint(
                fields=['journey', 'course'],
                condition=Q(course__isnull=False),
                name='uniq_ljnode_journey_course',
            ),
        ]
        indexes = [
            models.Index(fields=['journey']),
        ]

    def __str__(self):
        if self.course_bundle_id:
            return f'{self.journey_id}: bundle {self.course_bundle_id}'
        return f'{self.journey_id}: course {self.course_id}'


class LearningJourneyEdge(models.Model):
    """Directed edge from prerequisite node to dependent node within one journey."""

    journey = models.ForeignKey(
        LearningJourney,
        on_delete=models.CASCADE,
        related_name='edges',
    )
    from_node = models.ForeignKey(
        LearningJourneyNode,
        on_delete=models.CASCADE,
        related_name='out_edges',
    )
    to_node = models.ForeignKey(
        LearningJourneyNode,
        on_delete=models.CASCADE,
        related_name='in_edges',
    )

    class Meta:
        db_table = 'LearningJourneyEdge'
        verbose_name = 'Learning Journey Edge'
        verbose_name_plural = 'Learning Journey Edges'
        constraints = [
            models.UniqueConstraint(
                fields=['journey', 'from_node', 'to_node'],
                name='uniq_learningjourneyedge_journey_from_to',
            ),
            _edge_no_self_loop_constraint(),
        ]
        indexes = [
            models.Index(fields=['journey']),
            models.Index(fields=['from_node']),
            models.Index(fields=['to_node']),
        ]

    def __str__(self):
        return f'{self.from_node_id} → {self.to_node_id}'


class LearningJourneyEnrollment(models.Model):
    """Member opted into this journey (commit); delete row to uncommit."""

    journey = models.ForeignKey(
        LearningJourney,
        on_delete=models.CASCADE,
        related_name='enrollments',
    )
    community_member = models.ForeignKey(
        CommunityMember,
        on_delete=models.CASCADE,
        related_name='learning_journey_enrollments',
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'LearningJourneyEnrollment'
        verbose_name = 'Learning Journey Enrollment'
        verbose_name_plural = 'Learning Journey Enrollments'
        constraints = [
            models.UniqueConstraint(
                fields=['journey', 'community_member'],
                name='uniq_learningjourneyenrollment_journey_member',
            ),
        ]
        indexes = [
            models.Index(fields=['journey']),
            models.Index(fields=['community_member']),
        ]

    def __str__(self):
        return f'{self.community_member_id} → journey {self.journey_id}'
