django-postgres-metrics
=======================

A Django application that exposes a bunch of PostgreSQL database metrics.

Background
----------

At `PyCon Canada 2017 <https://2017.pycon.ca/>`__ `Craig Kerstiens
<http://www.craigkerstiens.com/>`__ gave a talk "`Postgres at any scale
<https://2017.pycon.ca/schedule/56/>`__". In his talk Craig pointed out a bunch
of metrics one should look at to understand why a PostgreSQL database could be
"slow" or not perform as expected.

This project adds a Django Admin view exposing these metrics to Django users
with the ``is_superusers`` flag turned on.

Installation
------------

Start by installing ``django-postgres-metrics`` from PyPI::

    $ pip install django-postgres-metrics

You will also need to make sure to have ``psycopg2`` or ``psycopg2-binary``
installed which is already a requirement by Django for PostgreSQL support
anyway.

Then you need to add ``postgres_metrics`` to your ``INSTALLED_APPS`` list. Due
to the wait postgres_metrics works, you need to include it *before* the
``admin`` app::

    INSTALLED_APPS = [
        'postgres_metrics.apps.PostgresMetrics',
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
    ]

Lastly, you need to add a URL path to your global ``urls.py`` *before* the
``admin`` URL patterns.

For Django 2.0 and up::

    from django.urls import include, path
    urlpatterns = [
        path('admin/postgres-metrics/', include('postgres_metrics.urls')),
        path('admin/', admin.site.urls),
    ]

For Django 1.11 and before::

    from django.conf.urls import include, url
    urlpatterns = [
        url(r'^admin/postgres-metrics/', include('postgres_metrics.urls')),
        url(r'^admin/', admin.site.urls),
    ]

Security
--------

If you found or if you think you found a security issue please get in touch via
``info+django-postgres-stats *AT* markusholtermann *DOT* eu``.

I'm working about this in my free time. I don't have time to monitor the email
24/7. But you should normally receive a response within a week. If I haven't
got back to you within 2 weeks, please reach out again.

TESTING
-------

To run the unit tests::

    $ pip install tox
    $ tox
