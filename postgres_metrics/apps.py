from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PostgresMetrics(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "postgres_metrics"
    verbose_name = _("PostgreSQL Metrics")
