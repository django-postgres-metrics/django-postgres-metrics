from django.core.exceptions import PermissionDenied
from django.db import connections
from django.http import Http404
from django.shortcuts import render

from .metrics import registry as metrics_registry


class MetricResult:

    def __init__(self, connection, name):
        self._connection = connection
        self._get_metrics(name)

    @property
    def alias(self):
        return self._connection.alias

    @property
    def dsn(self):
        return self._connection.connection.dsn

    def _get_metrics(self, metric):
        with self._connection.cursor() as cursor:
            cursor.execute(metric.sql)
            self.headers = [c.name.replace('-', ' ') for c in cursor.description]
            self.records = cursor.fetchall()


def metrics_view(request, name):
    if not request.user or not request.user.is_superuser:
        raise PermissionDenied

    if name not in metrics_registry:
        raise Http404

    metric = metrics_registry[name]

    context = {
        'metric': metric,
        'results': [],
    }

    for connection in connections.all():
        if connection.vendor != 'postgresql':
            continue
        db = MetricResult(connection, metric)
        context['results'].append(db)

    return render(request, 'postgres_metrics/table.html', context=context)
