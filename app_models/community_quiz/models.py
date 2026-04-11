from django.db import models
from app_models.community.models import Community, CommunityGroup
from app_models.account.models import User


class SimpleQuiz(models.Model):
    """
    Simple Quiz (MCQ) for a community — tier access via payment_plans.
    Physical table: ``SimpleQuiz``.
    """
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name='simple_quizzes',
        help_text='Community this quiz belongs to',
    )
    title = models.CharField(max_length=255, help_text='Title of the quiz')
    description = models.TextField(blank=True, null=True, help_text='Description of the quiz')
    quiz_data = models.TextField(help_text='JSON string containing quiz questions and structure')
    is_timed = models.BooleanField(default=False, help_text='Whether this quiz is timed (has a time limit)')
    has_attempt_limit = models.BooleanField(default=False, help_text='Whether this quiz has a limit on the number of attempts')
    max_attempts = models.PositiveIntegerField(null=True, blank=True, help_text='Maximum number of attempts allowed if has_attempt_limit is True')
    payment_plans = models.ManyToManyField(
        CommunityGroup,
        related_name='simple_quizzes',
        blank=True,
        help_text='Community groups (tiers) that have access to this quiz. Owners and co-owners have access regardless of tier.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'SimpleQuiz'
        verbose_name = 'Simple Quiz'
        verbose_name_plural = 'Simple Quizzes'
        ordering = ['-created_at']

    def clean(self):
        if self.max_attempts == 0:
            self.has_attempt_limit = False

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.community.name}"


class SimpleQuizGenerationJob(models.Model):
    """
    AI job row for generating a Simple Quiz. Shared queue table ``QuizGenerationJob``
    (future Custom Quiz jobs may use the same table with a discriminator or a separate model).
    """
    job_id = models.CharField(max_length=36, unique=True, help_text='Unique job identifier (GUID/UUID)')
    meta_data = models.TextField(
        help_text='JSON string containing job metadata (title, description, communityId, totalNumberOfQuestions, totalNumberOfMultipleChoice, totalNumberOfSingleChoice, isTimed, hasAttemptLimit, maxAttempts)'
    )
    file_url = models.CharField(max_length=500, help_text='Path to file in storage bucket containing notes for quiz generation')
    status = models.CharField(
        max_length=20,
        choices=[
            ('queued', 'Queued'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='queued',
        help_text='Status of the quiz generation job',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True, help_text='When the job was completed')

    class Meta:
        db_table = 'QuizGenerationJob'
        verbose_name = 'Simple Quiz Generation Job'
        verbose_name_plural = 'Simple Quiz Generation Jobs'
        ordering = ['-created_at']

    def __str__(self):
        return f"Job {self.job_id} - {self.status}"


class SimpleQuizSubmission(models.Model):
    """
    Attempt/results for a Simple Quiz. Physical table: ``SimpleQuizSubmission``.
    ``quiz`` may be null after the quiz definition is deleted; ``community`` and snapshots retain history.
    """
    quiz = models.ForeignKey(
        SimpleQuiz,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='submissions',
        help_text='Quiz that was submitted (null if the quiz was later deleted)',
    )
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name='simple_quiz_submissions',
        help_text='Community this attempt belongs to (denormalized for history after quiz delete)',
    )
    quiz_title_snapshot = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text='Quiz title at submission time',
    )
    quiz_id_at_submit = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Quiz primary key at submission time (for reference after delete)',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='simple_quiz_submissions',
        help_text='User who submitted the quiz',
    )
    submission_data = models.TextField(help_text='JSON string containing submission data with questions answered, correct/incorrect answers')
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text='Score achieved (percentage)')
    total_questions = models.IntegerField(help_text='Total number of questions in the quiz')
    correct_answers = models.IntegerField(default=0, help_text='Number of correct answers')
    incorrect_answers = models.IntegerField(default=0, help_text='Number of incorrect answers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'SimpleQuizSubmission'
        verbose_name = 'Simple Quiz Submission'
        verbose_name_plural = 'Simple Quiz Submissions'
        ordering = ['-created_at']

    def __str__(self):
        title = self.quiz_title_snapshot or (self.quiz.title if self.quiz else 'Deleted quiz')
        return f"{self.user.email} - {title} - {self.created_at}"
