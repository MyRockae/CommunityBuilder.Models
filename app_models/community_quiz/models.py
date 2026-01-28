from django.db import models
from app_models.community.models import Community, PaymentPlan
from app_models.account.models import User


class Quiz(models.Model):
    """Quiz model for community - associated with payment plans for access control"""
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='quizzes', help_text='Community this quiz belongs to')
    title = models.CharField(max_length=255, help_text='Title of the quiz')
    description = models.TextField(blank=True, null=True, help_text='Description of the quiz')
    quiz_data = models.TextField(help_text='JSON string containing quiz questions and structure')
    is_timed = models.BooleanField(default=False, help_text='Whether this quiz is timed (has a time limit)')
    has_attempt_limit = models.BooleanField(default=False, help_text='Whether this quiz has a limit on the number of attempts')
    max_attempts = models.PositiveIntegerField(null=True, blank=True, help_text='Maximum number of attempts allowed if has_attempt_limit is True')
    payment_plans = models.ManyToManyField(PaymentPlan, related_name='quizzes', blank=True, help_text='Payment plans that have access to this quiz. Owners and co-owners have access regardless of payment plan.')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'Quiz'
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quizzes'
        ordering = ['-created_at']
    
    def clean(self):
        """Validate that has_attempt_limit is False when max_attempts is 0"""
        if self.max_attempts == 0:
            self.has_attempt_limit = False
    
    def save(self, *args, **kwargs):
        """Override save to ensure has_attempt_limit is False when max_attempts is 0"""
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.title} - {self.community.name}"


class QuizGenerationJob(models.Model):
    """Quiz generation job model - used by background AI job to generate quiz questions"""
    job_id = models.CharField(max_length=36, unique=True, help_text='Unique job identifier (GUID/UUID)')
    meta_data = models.TextField(help_text='JSON string containing job metadata (title, description, communityId, totalNumberOfQuestions, totalNumberOfMultipleChoice, totalNumberOfSingleChoice, isTimed, hasAttemptLimit, maxAttempts)')
    file_url = models.CharField(max_length=500, help_text='Path to file in storage bucket containing notes for quiz generation')
    status = models.CharField(
        max_length=20,
        choices=[
            ('queued', 'Queued'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed')
        ],
        default='queued',
        help_text='Status of the quiz generation job'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True, help_text='When the job was completed')
    
    class Meta:
        db_table = 'QuizGenerationJob'
        verbose_name = 'Quiz Generation Job'
        verbose_name_plural = 'Quiz Generation Jobs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Job {self.job_id} - {self.status}"


class QuizSubmission(models.Model):
    """Quiz submission model - stores user quiz attempts and results"""
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='submissions', help_text='Quiz that was submitted')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_submissions', help_text='User who submitted the quiz')
    submission_data = models.TextField(help_text='JSON string containing submission data with questions answered, correct/incorrect answers')
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text='Score achieved (percentage)')
    total_questions = models.IntegerField(help_text='Total number of questions in the quiz')
    correct_answers = models.IntegerField(default=0, help_text='Number of correct answers')
    incorrect_answers = models.IntegerField(default=0, help_text='Number of incorrect answers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'QuizSubmission'
        verbose_name = 'Quiz Submission'
        verbose_name_plural = 'Quiz Submissions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.quiz.title} - {self.created_at}"
