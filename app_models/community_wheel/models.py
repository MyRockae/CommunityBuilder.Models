from django.db import models
from app_models.account.models import User
from app_models.community.models import Community


class Wheel(models.Model):
    """
    A structured, sequential community workflow. Owner/moderator sets the request
    message and ordered participants; each participant does the action for the next
    in sequence; anyone in the wheel can acknowledge; flow continues until complete.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('open_for_join', 'Open for Join'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    WHEEL_MODE_CHOICES = [
        ('chain', 'Chain (sequential one-to-next)'),
        ('collective', 'Collective support (all-for-one rotation)'),
    ]

    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name='wheels',
        help_text='Community this wheel belongs to',
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_wheels',
        help_text='Owner or moderator who created the wheel',
    )
    title = models.CharField(max_length=255, blank=True, null=True, help_text='Optional short name for the wheel')
    request_message = models.TextField(help_text='The instruction (e.g. pay 200$, send a gift)')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        db_index=True,
    )
    mode = models.CharField(
        max_length=20,
        choices=WHEEL_MODE_CHOICES,
        default='chain',
        help_text='Wheel mode: chain (each member acts for the next) or collective (all act for one, then rotate)',
    )
    max_favor_duration_days = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Maximum time a participant has to fulfil a wheel favour (in days, decimal allowed, e.g. 0.2)',
    )
    max_members = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text='Optional max participants when joining via link',
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text='Optional notes for the wheel',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Wheel'
        verbose_name = 'Wheel'
        verbose_name_plural = 'Wheels'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title or f'Wheel {self.id}'} - {self.community.name}"


class WheelParticipant(models.Model):
    """Ordered participant in a wheel. Each has a position and optional preference message."""
    APPROVAL_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    wheel = models.ForeignKey(
        Wheel,
        on_delete=models.CASCADE,
        related_name='participants',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wheel_participations',
    )
    order = models.PositiveIntegerField(help_text='Position in sequence (1 = first, 2 = second, ...)')
    preference_message = models.TextField(
        blank=True,
        null=True,
        help_text='Member reference info (e.g. account number) for the person doing the request for them',
    )
    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        default='pending',
        help_text='Participant approval status (e.g. pending until they accept / are approved)',
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_wheel_joins',
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'WheelParticipant'
        verbose_name = 'Wheel Participant'
        verbose_name_plural = 'Wheel Participants'
        ordering = ['wheel', 'order']
        unique_together = [
            ['wheel', 'user'],
            ['wheel', 'order'],
        ]

    def __str__(self):
        return f"{self.user.email} in wheel {self.wheel_id} (order {self.order})"


class WheelHandoff(models.Model):
    """
    One step in the wheel: from_participant does the request for to_participant.
    Anyone in the wheel can acknowledge; acknowledged_by tracks who did.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('action_done', 'Action Done'),
        ('acknowledged', 'Acknowledged'),
    ]

    wheel = models.ForeignKey(
        Wheel,
        on_delete=models.CASCADE,
        related_name='handoffs',
    )
    from_participant = models.ForeignKey(
        WheelParticipant,
        on_delete=models.CASCADE,
        related_name='handoffs_given',
        help_text='Participant who does the request',
    )
    to_participant = models.ForeignKey(
        WheelParticipant,
        on_delete=models.CASCADE,
        related_name='handoffs_received',
        help_text='Participant who receives',
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True,
    )
    note = models.TextField(
        blank=True,
        null=True,
        help_text='Optional evidence note from the giver',
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    acknowledged_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='wheel_handoff_acknowledgements',
        help_text='User (anyone in the wheel) who acknowledged this handoff',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'WheelHandoff'
        verbose_name = 'Wheel Handoff'
        verbose_name_plural = 'Wheel Handoffs'
        ordering = ['wheel', 'from_participant__order']
        unique_together = [['wheel', 'from_participant']]

    def __str__(self):
        return f"Wheel {self.wheel_id}: {self.from_participant_id} → {self.to_participant_id} ({self.status})"


class WheelHandoffAttachment(models.Model):
    """Evidence attachment (image/video) for a handoff."""
    FILE_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]

    wheel_handoff = models.ForeignKey(
        WheelHandoff,
        on_delete=models.CASCADE,
        related_name='attachments',
    )
    file_url = models.URLField(help_text='URL of the attached file')
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'WheelHandoffAttachment'
        verbose_name = 'Wheel Handoff Attachment'
        verbose_name_plural = 'Wheel Handoff Attachments'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.file_type} for handoff {self.wheel_handoff_id}"
