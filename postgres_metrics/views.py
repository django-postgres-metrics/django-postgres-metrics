from django.contrib.admin.views.main import ORDER_VAR
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import render

from .metrics import registry as metrics_registry


def metrics_view(request, name):
    if not request.user.is_superuser:
        raise PermissionDenied

    try:
        Metric = metrics_registry[name]
    except KeyError:
        raise Http404

    ordering = request.GET.get(ORDER_VAR)
    metric = Metric(ordering)

    return render(request, 'postgres_metrics/table.html', {
        'metric': metric,
        'results': metric.get_data(),
    })
