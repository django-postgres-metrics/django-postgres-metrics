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

.. figure:: _static/screenshot.png
    :target: _static/screenshot.png
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

.. code-block:: bash

    $ ./manage.py pgm_list_metrics
    ┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃ Slug                 ┃ Label                ┃ Description                                                                   ┃
    ┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
    │ available-extensions │ Available Extensions │ PostgreSQL can be extended by installing extensions with the CREATE           │
    │                      │                      │ EXTENSION command. The list of available extensions on each database is       │
    │                      │                      │ shown below.                                                                  │
    │ cache-hits           │ Cache Hits           │ The typical rule for most applications is that only a fraction of its data    │
    │                      │                      │ is regularly accessed. As with many other things data can tend to follow      │
    │                      │                      │ the 80/20 rule with 20% of your data accounting for 80% of the reads and      │
    ...
    └──────────────────────┴──────────────────────┴───────────────────────────────────────────────────────────────────────────────┘


``pgm_show_metric``
~~~~~~~~~~~~~~~~~~~

This command shows the metric's data. The command expects the ``slug`` from the
``pgm_list_metrics`` command output as the first argument.

.. code-block:: bash

    $ ./manage.py pgm_show_metric available-extensions
                                                    default (user=someuser dbname=somedb)
    ┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃ name               ┃ default version ┃ installed version ┃ comment                                                                ┃
    ┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
    │ adminpack          │ 2.1             │ None              │ administrative functions for PostgreSQL                                │
    │ amcheck            │ 1.2             │ None              │ functions for verifying relation integrity                             │
    │ autoinc            │ 1.0             │ None              │ functions for autoincrementing fields                                  │
    ...
    │ xml2               │ 1.1             │ None              │ XPath querying and XSLT                                                │
    └────────────────────┴─────────────────┴───────────────────┴────────────────────────────────────────────────────────────────────────┘
                                                   second (user=otheruser dbname=otherdb)
    ┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃ name               ┃ default version ┃ installed version ┃ comment                                                                ┃
    ┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
    │ adminpack          │ 2.1             │ None              │ administrative functions for PostgreSQL                                │
    │ amcheck            │ 1.2             │ None              │ functions for verifying relation integrity                             │
    │ autoinc            │ 1.0             │ None              │ functions for autoincrementing fields                                  │
    ...
    │ xml2               │ 1.1             │ None              │ XPath querying and XSLT                                                │
    └────────────────────┴─────────────────┴───────────────────┴────────────────────────────────────────────────────────────────────────┘
