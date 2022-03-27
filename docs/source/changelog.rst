=========
Changelog
=========

.. currentmodule:: postgres_metrics

Under Development
=================

0.13.0 (2022-03-27)
===================

* Dropped official support for Python 3.5.

  .. warning::

     Use version 0.12 for Python 3.5 support!

* Add the ``pgm_list_metrics`` and ``pgm_show_metric`` management commands.

0.12.0 (2022-03-25)
===================

* Dropped official support for Django 3.0 and 3.1.

  .. warning::

     Use version 0.11 for Django 3.0 or 3.1 support!

* Loosened the requirements for psycopg2 on Django 3.1 and above. There's no
  need to limit to ``psycopg2<2.9`` anymore.

0.11.0 (2021-10-06)
===================

* Added support for PostgreSQL 14.

* Added support for Django 4.0 and Python 3.10.

* Added dark-mode support. (`PR #59
  <https://github.com/django-postgres-metrics/django-postgres-metrics/pull/59>`_)

* Fixed several accessibility issues. (`PR #58
  <https://github.com/django-postgres-metrics/django-postgres-metrics/pull/58>`_)

0.10.1 (2021-04-06)
===================

* Use `pre-commit.ci <https://results.pre-commit.ci/repo/github/111322592>`_ for linting

* Use a single workflow file

0.10.0 (2021-03-01)
===================

* Use humanized sorting in the :class:`Index Size <metrics.IndexSize>` and
  :class:`Table Size <metrics.TableSize>` metrics.

* Extended the :class:`Table Size <metrics.TableSize>` metric with additional
  information.

0.9.0 (2021-01-05)
==================

* Added support for translatable column titles.

* Added support for metrics to only be available on certain PostgreSQL versions.

* Fixed an issue in the :class:`Cache Hits <metrics.CacheHits>` metric when a
  database doesn't track those metrics.

0.8.0 (2021-01-03)
==================

* Dropped support for Django 1.11, 2.0, and 2.1.

  .. warning::

     Use version 0.7 for Django 1.11, 2.0, or 2.1 support!

* Added a :class:`Sequence Usage <metrics.SequenceUsage>`
  that shows the extend to which a PostgreSQL sequence is been used.

* Added a screenshot of what a metric looks like to the README and docs (`#39
  <https://github.com/django-postgres-metrics/django-postgres-metrics/issues/39>`_
  ).

0.7.2 (2020-12-22)
==================

* Fixed layout issues in Django's admin before 3.1.

0.7.1 (2020-12-22)
==================

* Fixed layout issues with Django's new admin design in 3.1.

0.7.0 (2020-12-20)
==================

* Updated project setup by moving to GitHub Actions

* Added compatibility for Django 1.11 to 3.1

  .. warning::

     This is the last version to support Django < 2.2. Version 0.8 will only
     support Django 2.2, 3.0, and 3.1!

0.6.2 (2018-03-20)
==================

* Added missing installation instruction.

* Documentation building is now part of the CI tests.

0.6.1 (2018-03-20)
==================

* Fix release bundling.

0.6.0 (2018-03-20)
==================

* Added permission support for metrics. Users with ``is_staff=True`` can now
  be given access to each metric individually.

* The :func:`~templatetags.postgres_metrics.get_postgres_metrics` template tag
  now returns only metrics the current user (taken from the ``request`` object
  in the template context) has access to. This means the
  ``'django.template.context_processors.request'`` context processor is now
  required.

* The documentation now has an intersphinx setup to Python 3 and Django

* The hard dependency on psycopg2 was dropped because installing wheel files
  of psycopg2 can be troublesome `as outlined by the project maintainers
  <http://initd.org/psycopg/articles/2018/02/08/psycopg-274-released/>`__. When
  using django-postgres-metrics you now need to install psycopg2 or
  psycopg2-binary explicitly. This is usually not an issue as either one is
  required by Django anyway to use Django's PostgreSQL database backend.

* Added a :class:`Detailed Index Usage metric <metrics.DetailedIndexUsage>`
  that shows the index usage off a table per index.

0.5.0 (2017-12-25)
==================

* Added the list of metrics on a metric's detail page

0.4.0 (2017-12-25)
==================

* Underscores in metric column headers are now replaced by spaces

* The :class:`~metrics.IndexUsage` now shows floating point percentages

* Added :class:`~metrics.IndexSize` and :class:`~metrics.TableSize`

* Added per metric record and record item styling

0.3.0 (2017-11-28)
==================

* Added description to ``setup.py``

* The metric results can now be sorted on any column

0.2.0 (2017-11-21)
==================

* Switched to `Read The Docs <https://github.com/rtfd/sphinx_rtd_theme>`__
  theme for docs.

* Added "Available Extensions" metric.

* Fixed table styling in metric views. The tables now look more like Django
  Admin's ChangeList

0.1.1 (2017-11-21)
==================

* Excluded ``tests`` from built packages.

0.1.0 (2017-11-21)
==================

* Initial Release
