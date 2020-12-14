from django import template

from ..metrics import registry as metrics_registry

register = template.Library()


@register.simple_tag(takes_context=True)
def get_postgres_metrics(context):
    """
    Return an iterable over all registered metrics, sorted by their label.

    The template tag will filter out all metrics the current user does not
    have access to.

    See :class:`MetricRegistry.sorted
    <postgres_metrics.metrics.MetricRegistry.sorted>` for details.
    """
    user = context["request"].user
    for metric in metrics_registry.sorted:
        if metric.can_view(user):
            yield metric


@register.simple_tag(takes_context=True)
def record_style(context):
    """
    Return the style to be usd for the metric's current record.

    This expects a template context variable ``'metric'`` referring to the
    metric instance in question, as well as a context variable ``'record'``
    containing the current record to be used for style determination.

    This template tag calls into :class:`Metric.get_record_style
    <postgres_metrics.metrics.Metric.get_record_style>` and will---if a return
    value was specified---prefix that one with ``'pgm-'``.
    """
    metric = context["metric"]
    record = context["record"]
    style = metric.get_record_style(record)
    if style:
        return "pgm-%s" % style
    return ""


@register.simple_tag(takes_context=True)
def record_item_style(context):
    """
    Return the style to be usd for the metric's current record specific item.

    Like the :func:`record_style` template tag, this expects a template context
    variable ``'metric'`` referring to the metric instance in question, as well
    as a context variable ``'record'`` containing the current record.
    Furthermore, the ``'forloop.counter0'`` context is expected with the
    current column index to be styled. This mean, for styling, unline on the
    SQL column numbering, columns are zero-indexed.

    This template tag calls into :class:`Metric.get_record_item_style
    <postgres_metrics.metrics.Metric.get_record_item_style>` and will---if a
    return value was specified---prefix that one with ``'pgm-'``.
    """
    metric = context["metric"]
    record = context["record"]
    index = context["forloop"]["counter0"]
    style = metric.get_record_item_style(record, record[index], index)
    if style:
        return "pgm-%s" % style
    return ""
