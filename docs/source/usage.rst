.. _usage:

Using django-postgres-metrics
=============================

.. _django-admin-integration:

Django Admin Integration
------------------------

When you now browse to the Django Admin with superuser permissions, you'll see
a "PostgreSQL Metrics" section at the bottom left, listing all available
metrics.

This is what a metric could look like:

.. figure:: _static/screenshot-view.png
    :target: _static/screenshot-view.png
    :alt: Screenshot of the "Detailed Index Usage" metric, with help text, and
       a table with rows for each index


.. _command-line-interface:

Command Line Interface
----------------------

While the Django Admin is often installed and used by many, there are numerous
projects that do not use it. For them, django-postgres-metrics 0.13 brings a
few management commands that provide the same information.


``pgm_list_metrics``
~~~~~~~~~~~~~~~~~~~~

This command lists all available metrics.

.. figure:: _static/screenshot-cmd-list.svg
    :target: _static/screenshot-cmd-list.svg
    :alt: Screenshot of the "pgm_list_metrics" command, showing all commands
       with their slug, label and description.


``pgm_show_metric``
~~~~~~~~~~~~~~~~~~~

This command shows the metric's data. The command expects the ``slug`` from the
``pgm_list_metrics`` command output as the first argument.

.. figure:: _static/screenshot-cmd-show.svg
    :target: _static/screenshot-cmd-show.svg
    :alt: Screenshot of the "pgm_show_metric" command. In this example, the
       output for the detailed index usage.
