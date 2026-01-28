from rest_framework.exceptions import APIException
from django.db import models

class Tag(models.Model):
    """Tag model for communities and user interests"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        from django.utils.text import slugify
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        app_label = 'shared'
        db_table = 'Tag'
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['name']

class InternalServerError(APIException):
    status_code = 500
    default_detail = "An unexpected error occurred. Please try again later."
    default_code = "internal_error"

    def __init__(self, detail=None):
        """
        Allow passing a custom error message.
        If no message is provided, use the default.
        """
        if detail is None:
            detail = self.default_detail
        super().__init__(detail)


class CustomWebApiException(APIException):
    status_code = 400
    default_detail = "Something went wrong."
    default_code = "server exception error"

    def __init__(self, error=None, code=None):
        # Use the passed-in error or fall back to the default
        if error is not None:
            self.detail = error
        else:
            self.detail = self.default_detail

        # Use the passed-in code or fall back to the default
        if code is not None:
            self.default_code = code

        super().__init__(self.detail, self.default_code)

    def get_full_details(self):

        return {
            "error": self.detail,
            "code": self.default_code
        }
