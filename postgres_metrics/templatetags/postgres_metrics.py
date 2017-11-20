from django import template

from ..metrics import registry as metrics_registry

register = template.Library()


@register.simple_tag
def get_postgres_metrics():
    return metrics_registry.sorted
