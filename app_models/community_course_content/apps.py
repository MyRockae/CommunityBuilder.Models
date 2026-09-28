from django.apps import AppConfig


class CommunityCourseContentConfig(AppConfig):
    default = True
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_models.community_course_content'
    label = 'community_course_content'
    verbose_name = 'Community Course Content'
