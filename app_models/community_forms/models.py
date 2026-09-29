import secrets

from django.core.exceptions import ValidationError
from django.db import models

from app_models.account.models import User
from app_models.community.models import Community
from app_models.community_forms.definition import FormDefinitionError, validate_definition


class FormAudience(models.TextChoices):
    MEMBERS = "members", "Community members"
    SIGNED_IN = "signed_in", "Signed-in users"
    ANYONE = "anyone", "Anyone with the link"


def _new_share_id() -> str:
    return secrets.token_urlsafe(16)[:32]


class CommunityForm(models.Model):
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name="forms",
        help_text="Community this form belongs to",
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_community_forms",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    share_id = models.CharField(
        max_length=32,
        unique=True,
        db_index=True,
        help_text="Unguessable public token used in the fill URL",
    )
    audience = models.CharField(
        max_length=16,
        choices=FormAudience.choices,
        default=FormAudience.MEMBERS,
    )
    is_open = models.BooleanField(default=True)
    one_response_per_user = models.BooleanField(default=True)
    definition = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "CommunityForm"
        verbose_name = "Community form"
        verbose_name_plural = "Community forms"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["community", "-created_at"], name="cform_community_created_idx"),
        ]

    def __str__(self):
        return f"{self.title} ({self.community_id})"

    def clean(self):
        try:
            self.definition = validate_definition(self.definition)
        except FormDefinitionError as exc:
            raise ValidationError({"definition": str(exc)}) from exc

    def save(self, *args, **kwargs):
        if not self.share_id:
            for _ in range(8):
                candidate = _new_share_id()
                if not CommunityForm.objects.filter(share_id=candidate).exists():
                    self.share_id = candidate
                    break
            else:
                self.share_id = secrets.token_urlsafe(24)[:32]
        self.clean()
        super().save(*args, **kwargs)


class CommunityFormResponse(models.Model):
    form = models.ForeignKey(
        CommunityForm,
        on_delete=models.CASCADE,
        related_name="responses",
    )
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name="form_responses",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="community_form_responses",
    )
    definition_snapshot = models.JSONField(default=dict)
    answers = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "CommunityFormResponse"
        verbose_name = "Community form response"
        verbose_name_plural = "Community form responses"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["form", "-created_at"], name="cform_resp_form_created_idx"),
            models.Index(fields=["community", "-created_at"], name="cform_resp_comm_created_idx"),
        ]

    def __str__(self):
        return f"response {self.pk} form={self.form_id}"
