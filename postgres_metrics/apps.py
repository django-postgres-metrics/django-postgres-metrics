from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PostgresMetrics(AppConfig):
    name = "postgres_metrics"
    verbose_name = _("PostgreSQL Metrics")
