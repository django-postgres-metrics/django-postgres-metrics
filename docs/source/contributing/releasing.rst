=====================
Issuing a new Release
=====================

* Update the changelog (:file:`docs/source/changelog.rst`) with the new
  desired version.

* Tag the new release and push it:

  .. code-block:: console

     $ git tag -s "x.y.z"
     $ git push --tags origin master

* Go to https://github.com/django-postgres-metrics/django-postgres-metrics/releases
  and click "Add release notes" for the newly pushed release, and update the
  release notes there as well.
