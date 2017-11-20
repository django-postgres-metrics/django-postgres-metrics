from django.db import connections
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import render

from .constants import STATS


class Statistic:

    def __init__(self, connection, name):
        self._connection = connection
        self._get_stats(name)

    def __repr__(self):
        return '<Database "%s">' % self._connection.alias

    @property
    def alias(self):
        return self._connection.alias

    @property
    def dsn(self):
        return self._connection.connection.dsn

    def _get_stats(self, name):
        with self._connection.cursor() as cursor:
            cursor.execute(STATS[name])
            self.headers = [c.name for c in cursor.description]
            self.records = cursor.fetchall()


def stats_view(request, name):
    if not request.user or not request.user.is_superuser:
        raise PermissionDenied

    if name not in STATS:
        raise Http404

    context = {
        'statistics': [],
        'stats_name': name,
    }

    for connection in connections.all():
        if connection.vendor != 'postgresql':
            continue
        db = Statistic(connection, name)
        context['statistics'].append(db)

    return render(request, 'postgres_stats/table.html', context=context)
