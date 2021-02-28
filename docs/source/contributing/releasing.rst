=====================
Issuing a new Release
=====================

* Update the changelog (:file:`docs/source/changelog.rst`) with the new
  desired version.

* Tag the new release and push it:

  .. code-block:: console

     $ git tag -s "x.y.z"
     $ git push --tags origin main

* `Update the release nodes
  <https://github.com/django-postgres-metrics/django-postgres-metrics/releases>`_
  on GitHub for the newly pushed release.

* Update the versions in `ReadTheDocs
  <https://readthedocs.org/projects/django-postgres-metrics/versions/>`_.
