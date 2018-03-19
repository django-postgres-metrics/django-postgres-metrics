Background. Why? What?
======================

The original idea for this library comes from `Craig Kerstiens
<http://www.craigkerstiens.com/>`__'s talk "`Postgres at any scale
<https://2017.pycon.ca/schedule/56/>`__" at `PyCon Canada 2017
<https://2017.pycon.ca/>`__. In his talk, Craig pointed out a bunch of metrics
one should look at to understand why a PostgreSQL database could be "slow" or
not perform as expected.

In many cases, the root cause for "PostgreSQL being slow" is the lack of
memory, full table scans, and others. For example, a cache hit ratio of less
than 99% means that each of cache miss queries needs to go to the filesystem.
Filesystem access is significantly slower than RAM access. Giving the
PostgreSQL instance more memory will very likely improve performance.

This project aims at showing these and other metrics in the Django Admin making
such bottlenecks visible.
