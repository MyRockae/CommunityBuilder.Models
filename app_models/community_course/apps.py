from django.apps import AppConfig


class CommunityCourseConfig(AppConfig):
    default = True
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_models.community_course'
    label = 'community_course'
    verbose_name = 'Community Course'
