=====================
Issuing a new Release
=====================

* Install ``bumpversion`` with::

     $ pip install git+ssh://git@github.com:MarkusH/bumpversion.git@sign#egg=bumpversion

* Install ``twine`` with::

     $ pip install twine

* Determine next version number from the ``changelog.rst`` (ensuring to follow
  `SemVer <http://semver.org/>`__)
* Ensure ``changelog.rst`` is representative with new version number and commit
  possible changes.
* Update the version number with ``bumpversion``::

     $ bumpversion $part

  (instead of ``$part`` you can use ``major``, ``minor``, or ``patch``.

* ``git push --tags origin master``
* Check for TravisCI to complete. If TravisCI fails due to code errors, go back
  to the start and bump the ``$part`` with ``patch``
* Build artifacts with::

     $ python setup.py sdist bdist_wheel

* Upload artifacts with::

     $ twine upload -s dist/*$newver*

* Add likely new version to at the top of ``changelog.rst``

* Go to https://github.com/django-postgres-metrics/django-postgres-metrics/tags
  and click "Add release notes" for the newly pushed release, and publish the
  release notes there as well.
