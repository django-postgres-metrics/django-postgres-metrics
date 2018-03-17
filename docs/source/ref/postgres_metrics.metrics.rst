Metrics
=======

.. currentmodule:: postgres_metrics.metrics

.. autoclass:: MetricRegistry
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: Metric
    :members:
    :undoc-members:
    :show-inheritance:

    .. attribute:: permission_name

        The codename for a :class:`~django.contrib.auth.models.Permission` that
        will grant a staff user access to the corresponding metric.

        The permission name has the form ``can_view_metric_$FOO`` where
        ``$FOO`` is the :attr:`~slug` with dashes (``-``) replaces by
        underscores (``_``).

    .. attribute:: permission_key

        For convenience when checking access to a metric, the permission key
        is ``postgres_metrics.$permission_name``.

.. autoclass:: MetricResult
    :undoc-members:
    :show-inheritance:

    .. not including :members: in `MetricResult` because they are documented in
       the class's docstring

.. autoclass:: MetricHeader
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: AvailableExtensions()

.. autoclass:: CacheHitsMetric()

.. autoclass:: IndexSizeMetric()

.. autoclass:: IndexUsageMetric()

.. autoclass:: TableSizeMetric()
