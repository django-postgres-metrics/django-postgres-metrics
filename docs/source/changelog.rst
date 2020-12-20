=========
Changelog
=========

.. currentmodule:: postgres_metrics

Under Development
=================

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
