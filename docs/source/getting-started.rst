Getting Started
===============

.. currentmodule:: postgres_metrics

Installation
------------

Start by installing ``django-postgres-metrics`` from PyPI:

.. code-block:: bash

    $ pip install django-postgres-metrics

You will also need to make sure to have ``psycopg2`` or ``psycopg2-binary``
installed which is already a requirement by Django for PostgreSQL support
anyway.

Then you need to add ``postgres_metrics`` to your ``INSTALLED_APPS`` list. Due
to the way postgres_metrics works, you need to include it *before* the
``admin`` app:

.. code-block:: python

    INSTALLED_APPS = [
        'postgres_metrics.apps.PostgresMetrics',
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
    ]

You also need to make sure that the ``request`` context processor is included
in the ``TEMPLATES`` setting. It is included by default for projects that were
started on Django 1.8 or later:

.. code-block:: python

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'OPTIONS': {
                'context_processors': [
                    ...,
                    'django.template.context_processors.request',
                    ...,
                ],
            },
        },
    ]

Lastly, you need to add a URL path to your global ``urls.py`` *before* the
``admin`` URL patterns.

.. code-block:: bash

    from django.urls import include, path
    urlpatterns = [
        path('admin/postgres-metrics/', include('postgres_metrics.urls')),
        path('admin/', admin.site.urls),
    ]

Congratulations, you made it!

Next, see the :ref:`Usage <usage>` section for the
:ref:`django-admin-integration` or the :ref:`command-line-interface`.
