from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from app_models.community.models import Community, PaymentPlan
from app_models.account.models import User


class MeetingSeries(models.Model):
    """
    Template for Teams-style recurring meetings. The API creates/updates Meeting rows
    per occurrence; this model stores recurrence rules and shared access (plans, attendees).
    """

    class RecurrenceFrequency(models.TextChoices):
        DAILY = 'daily', 'Daily'
        WEEKLY = 'weekly', 'Weekly'
        MONTHLY = 'monthly', 'Monthly'
        YEARLY = 'yearly', 'Yearly'

    class RecurrenceEndType(models.TextChoices):
        NEVER = 'never', 'Never'
        ON_DATE = 'on_date', 'On date'
        AFTER_COUNT = 'after_count', 'After count'

    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name='meeting_series',
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_meeting_series',
    )
    title = models.CharField(max_length=255, help_text='Meeting title')
    description = models.TextField(blank=True, null=True, help_text='Meeting description/notes')
    location = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text='Physical meeting location',
    )
    meeting_url = models.URLField(
        blank=True,
        null=True,
        help_text='Virtual meeting URL (Zoom, Google Meet, etc.)',
    )
    time_zone = models.CharField(
        max_length=64,
        default='UTC',
        help_text='IANA timezone name (e.g. America/New_York)',
    )
    recurrence_frequency = models.CharField(
        max_length=20,
        choices=RecurrenceFrequency.choices,
        help_text='How often occurrences repeat',
    )
    interval = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text='Every N days/weeks/months/years depending on frequency',
    )
    weekly_days = models.JSONField(
        null=True,
        blank=True,
        default=list,
        help_text='When frequency is weekly: non-empty list of ISO weekdays 1–7 (Mon=1 … Sun=7)',
    )
    recurrence_end_type = models.CharField(
        max_length=20,
        choices=RecurrenceEndType.choices,
        default=RecurrenceEndType.NEVER,
    )
    recurrence_end_date = models.DateField(
        null=True,
        blank=True,
        help_text='Last possible occurrence date in time_zone when end type is ON_DATE',
    )
    occurrence_count = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Total occurrences including the first when end type is AFTER_COUNT',
    )
    payment_plans = models.ManyToManyField(
        PaymentPlan,
        related_name='meeting_series',
        blank=True,
        help_text='Payment plans that have access to this series',
    )
    attendees = models.ManyToManyField(
        User,
        related_name='meeting_series_attending',
        blank=True,
        help_text='Users invited to occurrences in this series',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'MeetingSeries'
        verbose_name = 'Meeting Series'
        verbose_name_plural = 'Meeting Series'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['community', 'created_at']),
        ]

    def __str__(self):
        return f"{self.title} - {self.community.name}"

    def clean(self):
        if self.interval is not None and self.interval < 1:
            raise ValidationError({'interval': 'Interval must be at least 1.'})

        if self.recurrence_frequency == self.RecurrenceFrequency.WEEKLY:
            days = self.weekly_days
            if not days or not isinstance(days, list) or len(days) == 0:
                raise ValidationError(
                    {'weekly_days': 'Weekly recurrence requires a non-empty list of weekdays (1–7).'}
                )
            for d in days:
                if not isinstance(d, int) or d < 1 or d > 7:
                    raise ValidationError(
                        {'weekly_days': 'Each weekday must be an integer from 1 (Monday) through 7 (Sunday).'}
                    )
        else:
            if self.weekly_days and len(self.weekly_days) > 0:
                raise ValidationError(
                    {'weekly_days': 'weekly_days must be empty or null unless frequency is weekly.'}
                )

        if self.recurrence_end_type == self.RecurrenceEndType.NEVER:
            if self.recurrence_end_date is not None:
                raise ValidationError(
                    {'recurrence_end_date': 'Must be empty when end type is never.'}
                )
            if self.occurrence_count is not None:
                raise ValidationError(
                    {'occurrence_count': 'Must be empty when end type is never.'}
                )
        elif self.recurrence_end_type == self.RecurrenceEndType.ON_DATE:
            if self.recurrence_end_date is None:
                raise ValidationError(
                    {'recurrence_end_date': 'Required when end type is on date.'}
                )
            if self.occurrence_count is not None:
                raise ValidationError(
                    {'occurrence_count': 'Must be empty when end type is on date.'}
                )
        elif self.recurrence_end_type == self.RecurrenceEndType.AFTER_COUNT:
            if self.occurrence_count is None:
                raise ValidationError(
                    {'occurrence_count': 'Required when end type is after count.'}
                )
            if self.occurrence_count < 1:
                raise ValidationError(
                    {'occurrence_count': 'Occurrence count must be at least 1.'}
                )
            if self.recurrence_end_date is not None:
                raise ValidationError(
                    {'recurrence_end_date': 'Must be empty when end type is after count.'}
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Meeting(models.Model):
    """Meeting model for community meetings; may belong to a recurring MeetingSeries."""

    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='meetings')
    title = models.CharField(max_length=255, help_text='Meeting title')
    description = models.TextField(blank=True, null=True, help_text='Meeting description/notes')
    start_datetime = models.DateTimeField(help_text='Start date and time')
    end_datetime = models.DateTimeField(help_text='End date and time')
    location = models.CharField(max_length=500, blank=True, null=True, help_text='Physical meeting location')
    meeting_url = models.URLField(blank=True, null=True, help_text='Virtual meeting URL (Zoom, Google Meet, etc.)')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_meetings')
    series = models.ForeignKey(
        MeetingSeries,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='meetings',
        help_text='Recurring series this occurrence belongs to, if any',
    )
    series_sequence = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Stable ordering within a series (e.g. 1-based occurrence index)',
    )
    payment_plans = models.ManyToManyField(PaymentPlan, related_name='meetings', blank=True, help_text='Payment plans that have access to this meeting')
    attendees = models.ManyToManyField(User, related_name='meetings_attending', blank=True, help_text='Users invited to the meeting')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Meeting'
        verbose_name = 'Meeting'
        verbose_name_plural = 'Meetings'
        ordering = ['start_datetime']
        indexes = [
            models.Index(fields=['series', 'start_datetime'], name='Meeting_series_start_idx'),
            models.Index(fields=['community', 'start_datetime'], name='Meeting_community_start_idx'),
        ]

    def __str__(self):
        return f"{self.title} - {self.community.name}"
