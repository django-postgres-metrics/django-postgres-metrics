=========
Changelog
=========

.. currentmodule:: postgres_metrics

0.6.0 (under development)
=========================

* Added permission support for metrics. Users with ``is_staff=True`` can now
  be given access to each metric individually.

* The :func:`~templatetags.postgres_metrics.get_postgres_metrics` template tag
  now returns only metrics the current user (taken from the ``request`` object
  in the template context) has access to.

* The documentation now has an intersphinx setup to Python 3 and Django

0.5.0
=====

* Added the list of metrics on a metric's detail page

0.4.0
=====

* Underscores in metric column headers are now replaced by spaces

* The :class:`~metrics.IndexUsageMetric` now shows floating point percentages

* Added :class:`~metrics.IndexSizeMetric` and :class:`~metrics.TableSizeMetric`

* Added per metric record and record item styling

0.3.0
=====

* Added description to ``setup.py``

* The metric results can now be sorted on any column

0.2.0
=====

* Switched to `Read The Docs <https://github.com/rtfd/sphinx_rtd_theme>`_ theme
  for docs.

* Added "Available Extensions" metric.

* Fixed table styling in metric views. The tables now look more like Django
  Admin's ChangeList

0.1.1
=====

* Excluded ``tests`` from built packages.

0.1.0
=====

* Initial Release
