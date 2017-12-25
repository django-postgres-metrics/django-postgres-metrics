=========
Changelog
=========

.. currentmodule:: postgres_metrics

0.4.0 (under development)
=========================

* Underscores in metric column headers are now replaced by spaces

* The :class:`~metrics.IndexUsageMetric` now shows floating point percentages

* Added :class:`~metrics.IndexSizeMetric` and :class:`~metrics.TableSizeMetric`

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

* Inital Release
