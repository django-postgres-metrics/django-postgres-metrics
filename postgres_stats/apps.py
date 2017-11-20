from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PostgresStats(AppConfig):
    name = 'postgres_stats'
    verbose_name = _('PostgreSQL Statistics')
