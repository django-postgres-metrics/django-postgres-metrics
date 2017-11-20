from django import template

from ..constants import STATS

register = template.Library()


@register.simple_tag
def get_postgres_stats():
    return sorted(STATS)


@register.filter
def format_stats_name(value):
    return value.replace('-', ' ').replace('_', ' ')
