from django.db import connection
from django.http import Http404
from django.shortcuts import render

from .constants import STATS


def stats_view(request, name):
    if name not in STATS:
        raise Http404

    with connection.cursor() as cursor:
        cursor.execute(STATS[name])
        headers = [c.name.replace('_', ' ') for c in cursor.description]
        data = cursor.fetchall()

    context = {
        'result_headers': headers,
        'results': data,
        'stats_name': name,
    }

    return render(request, 'postgres_stats/table.html', context=context)
