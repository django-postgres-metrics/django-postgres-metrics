# django-postgres-metrics

![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/django-postgres-metrics/django-postgres-metrics/Lint%20&%20Test/master?style=for-the-badge)
![Codecov branch](https://img.shields.io/codecov/c/gh/django-postgres-metrics/django-postgres-metrics/master?style=for-the-badge)
![PyPI](https://img.shields.io/pypi/v/django-postgres-metrics?style=for-the-badge)

A Django application that exposes a bunch of PostgreSQL database metrics.

## Background

At [PyCon Canada 2017](https://2017.pycon.ca/) [Craig Kerstiens](http://www.craigkerstiens.com/)
gave a talk "[Postgres at any scale](https://2017.pycon.ca/schedule/56/)". In his talk Craig
pointed out a bunch of metrics one should look at to understand why a PostgreSQL database could
be "slow" or not perform as expected.

This project adds a Django Admin view exposing these metrics to Django users with the
`is_superusers` flag turned on.

## Installation

Start by installing `django-postgres-metrics` from PyPI:

```console
(env)$ python -m pip install django-postgres-metrics
```

You will also need to make sure to have `psycopg2` installed which is already a requirement by
Django for PostgreSQL support anyway.

Then you need to add `postgres_metrics` to your `INSTALLED_APPS` list. Due to the way
`django-postgres-metrics` works, you need to include it \_before\* the `admin` app:

```python
INSTALLED_APPS = [
    'postgres_metrics.apps.PostgresMetrics',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
```

You also need to make sure that the `request` context processor is included in the `TEMPLATES`
setting. It is included by default for projects that were started on Django 1.8 or later:

```python
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
```

Lastly, you need to add a URL path to your global `urls.py` _before_ the `admin` URL patterns.

For Django 2.0 and up:

```python
from django.urls import include, path

urlpatterns = [
    path('admin/postgres-metrics/', include('postgres_metrics.urls')),
    path('admin/', admin.site.urls),
]
```

For Django 1.11:

```python
from django.conf.urls import include, url

urlpatterns = [
    url(r'^admin/postgres-metrics/', include('postgres_metrics.urls')),
    url(r'^admin/', admin.site.urls),
]
```

## Security

If you found or if you think you found a security issue please get in touch via
`info+django-postgres-metrics *AT* markusholtermann *DOT* eu`.

I'm working about this in my free time. I don't have time to monitor the email 24/7. But you
should normally receive a response within a week. If I haven't got back to you within
2 weeks, please reach out again.

## Contributing

The uses [pre-commit](https://pre-commit.com/) for linting and formatting of source code:

```console
(env)$ python -m pip install '.[dev,test]'
(env)$ pre-commit install -t pre-commit -t pre-push --install-hooks
```

To run the unit tests:

```console
(env)$ django-admin.py test -v 2 --settings=tests.settings
```
