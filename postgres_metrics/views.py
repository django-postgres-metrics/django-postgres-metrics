from django.db import connections
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import render

from .constants import METRICS


class MetricResult:

    def __init__(self, connection, name):
        self._connection = connection
        self._get_metrics(name)

    def __repr__(self):
        return '<Database "%s">' % self._connection.alias

    @property
    def alias(self):
        return self._connection.alias

    @property
    def dsn(self):
        return self._connection.connection.dsn

    def _get_metrics(self, name):
        with self._connection.cursor() as cursor:
            cursor.execute(METRICS[name])
            self.headers = [c.name for c in cursor.description]
            self.records = cursor.fetchall()


def metrics_view(request, name):
    if not request.user or not request.user.is_superuser:
        raise PermissionDenied

    if name not in METRICS:
        raise Http404

    context = {
        'metrics': [],
        'metrics_name': name,
    }

    for connection in connections.all():
        if connection.vendor != 'postgresql':
            continue
        db = MetricResult(connection, name)
        context['metrics'].append(db)

    return render(request, 'postgres_metrics/table.html', context=context)
