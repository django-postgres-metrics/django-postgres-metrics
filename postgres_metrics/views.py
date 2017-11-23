from django.contrib.admin.views.main import ORDER_VAR
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import render

from .metrics import registry as metrics_registry


def metrics_view(request, name):
    if not request.user or not request.user.is_superuser:
        raise PermissionDenied

    if name not in metrics_registry:
        raise Http404

    Metric = metrics_registry[name]

    ordering = request.GET.get(ORDER_VAR)
    metric = Metric(ordering)

    context = {
        'metric': metric,
        'results': metric.get_data(),
    }

    return render(request, 'postgres_metrics/table.html', context=context)
