from django import template

from ..metrics import METRICS

register = template.Library()


@register.simple_tag
def get_postgres_metrics():
    return sorted(METRICS)


@register.filter
def format_metrics_name(value):
    return value.replace('-', ' ').replace('_', ' ')
