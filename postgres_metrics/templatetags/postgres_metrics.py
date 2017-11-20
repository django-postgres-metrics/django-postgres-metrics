from django import template

from ..metrics import registry as metrics_registry

register = template.Library()


@register.simple_tag
def get_postgres_metrics():
    return metrics_registry.names


@register.filter
def format_metrics_name(value):
    return value.replace('-', ' ').replace('_', ' ')
