import re

from django.core.exceptions import ImproperlyConfigured
from django.db import connections
from django.utils.encoding import force_text
from django.utils.functional import cached_property
from django.utils.html import escape, urlize
from django.utils.text import normalize_newlines, slugify
from django.utils.translation import ugettext_lazy as _


class MetricRegistry:

    def __init__(self):
        self._registry = {}

    def __contains__(self, slug):
        return slug in self._registry

    def __getitem__(self, slug):
        return self._registry[slug]

    def __iter__(self):
        return iter(self._registry.values())

    def register(self, metric):
        """
        Given a class (not class instance) of :class:`Metric`, adds it to the
        available list of metrics to show it to a user.
        """
        self._registry[metric.slug] = metric

    @property
    def sorted(self):
        """
        All registered metrics ordered by their label.
        """
        return sorted((m for m in self), key=lambda m: m.label)

    def unregister(self, slug):
        """
        Remove the metric ``slug`` from the registry. Raises a ``KeyError`` if
        the metric isn't registered.
        """
        del self._registry[slug]


registry = MetricRegistry()


class MetricHeader:
    """
    A single column header; mostly takes care of a column's sorting status.
    """

    def __init__(self, name, index, ordering):
        self.name = name.replace('-', ' ')
        self.index = index
        self.ordering = ordering

    def __repr__(self):
        return '<MetricHeader "%s">' % self.name

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return (
            self.name == other.name and
            self.index == other.index and
            self.ordering == other.ordering
        )

    @staticmethod
    def join_ordering(ordering):
        return '.'.join('%s%d' % o for o in ordering)

    @cached_property
    def ascending(self):
        """``True`` if the column is in ascending order ``False`` otherwise"""
        for index, (direction, column) in enumerate(self.ordering, start=1):
            if column == self.index and direction == '':
                return True
        return False

    @cached_property
    def sort_priority(self):
        """The priority of the columns order. 1 (high), n(low). Default 0."""
        for index, (direction, column) in enumerate(self.ordering, start=1):
            if column == self.index:
                return index
        return 0

    @cached_property
    def url_primary(self):
        """Querystring value making this the primary sorting header."""
        return MetricHeader.join_ordering(
            [('-' if self.ascending else '', self.index)] +
            [
                (direction, column)
                for direction, column in self.ordering
                if column != self.index
            ],
        )

    @cached_property
    def url_remove(self):
        """Querystring value removing this column from sorting."""
        return MetricHeader.join_ordering(
            (direction, column)
            for direction, column in self.ordering
            if column != self.index
        )

    @cached_property
    def url_toggle(self):
        """Querystring value toggling ascending/descending for this header."""
        return MetricHeader.join_ordering(
            (
                direction
                if column != self.index
                else
                ('' if direction else '-'),
                column,
            )
            for direction, column in self.ordering
        )


class MetricResult:
    """
    Hold a metric's data for a single database.

    .. attribute:: alias

       The alias under which a database connection is known to Django.

    .. attribute:: dsn

       The PostgreSQL connection string per `psycopg2
       <http://initd.org/psycopg/docs/connection.html#connection.dsn>`_.

    .. attribute:: records

       The rows returned by a metric for the given database.
    """

    __slots__ = (
        'alias', 'dsn', 'records',
    )

    def __init__(self, connection, records):
        self.alias = connection.alias
        self.dsn = connection.connection.dsn
        self.records = records


class MetricMeta(type):

    def __new__(mcs, name, bases, attrs):
        if bases:
            # Only subclasses of `Metric`
            if not attrs.get('label'):
                attrs['label'] = name
            if not attrs.get('slug'):
                attrs['slug'] = slugify(attrs['label'])
            if not attrs.get('sql'):
                msg = 'Metric "%s" is missing a "sql" attribute or "sql" is empty.'
                raise ImproperlyConfigured(msg % name)

            docstring = attrs.get('__doc__')
            if docstring:
                docstring = normalize_newlines(force_text(docstring))
                docstring = '\n'.join(line.strip() for line in docstring.split('\n'))
                paras = re.split('\n{2,}', docstring)
                paras = [
                    '<p>%s</p>' % urlize(escape(p).replace('\n', ' ').strip())
                    for p in paras
                ]
                attrs['description'] = '\n\n'.join(paras)
            else:
                attrs['description'] = ''

        return super().__new__(mcs, name, bases, attrs)


class Metric(metaclass=MetricMeta):
    """
    The superclass for all Metric implementations. Inherit from this to define
    your own metric.

    If you want to implement your own metric, here's a gist::

       from django.utils.translation import ugettext_lazy as _
       from postgres_metrics.metrics import Metric, registry


       class DjangoMigrationStatistics(Metric):
           \"\"\"
           Count the number of applied Django migrations per app and sort by
           descending count and ascending app name.
           \"\"\"
           label = _('Migration Statistics')
           slug = 'django-migration-statistics'
           ordering = '-2.1'
           sql = '''
               SELECT
                   app, count(*)
               FROM
                   django_migrations
               GROUP BY
                   app
               {ORDER_BY}
               ;
           '''


       registry.register(DjangoMigrationStatistics)

    .. attribute:: description

       Don't define this value directly. Instead define a docstring on the
       metric class.

       The docstring will be processed by Python internals to trim leading
       white spaces and fix newlines. ``'\\r\\n'`` and ``'\\r'`` line breaks will
       be normalized to ``'\\n'``. Two or more consecutive occurances of
       ``'\\n'`` mark a paragraph which will be escaped and wrapped in
       ``<p></p>`` HTML tags. Further, each paragraph will call into Django's
       ``urlize()`` method to create ``<a></a>`` HTML tags around links.
    """

    #: The label is what is used in the Django Admin views. Consider marking
    #: this string as translateable.
    label = ''

    #: The default ordering that should be applied to the SQL query by default.
    #: This needs to be a valid ordering string as defined on
    #: :attr:`parsed_ordering`.
    ordering = ''

    #: A URL safe representation of the label and unique across all metrics.
    slug = ''

    #: The actual SQL statement that is being used to query the database. In
    #: order to make use of the :attr:`ordering`, include the string
    #: ``{ORDER_BY}`` in the query as necessary. For details on that value see
    #: :meth:`get_order_by_clause`.
    sql = ''

    def __init__(self, ordering=None):
        self.ordering = ordering or self.ordering

    @cached_property
    def full_sql(self):
        """
        The :attr:`sql` formatted with :meth:`get_order_by_clause`.
        """
        return self.sql.format(ORDER_BY=self.get_order_by_clause())

    def get_data(self):
        """
        Iterate over all configured PostgreSQL database and execute the
        :attr:`full_sql` there.

        :return: Returns a list of :class:`MetricResult` instances.
        :rtype: list
        """
        results = []
        for connection in connections.all():
            if connection.vendor != 'postgresql':
                continue
            with connection.cursor() as cursor:
                cursor.execute(self.full_sql)
                self.headers = [
                    MetricHeader(c.name, index, self.parsed_ordering)
                    for index, c in enumerate(cursor.description, start=1)
                ]
                data = cursor.fetchall()
            db = MetricResult(connection, data)
            results.append(db)
        return results

    @cached_property
    def parsed_ordering(self):
        """
        Turn an ordering string like ``1.5.-3.-2.6`` into the respective abstraction.

        Given :attr:`self.ordering` as ``1.5.-3.-2.6`` return a lis of 2-tuples
        like ``[('', 1), ('', 5), ('-', 3), ('-', 2), ('', 6)]``.
        """
        if self.ordering:
            return [
                ('-' if o.startswith('-') else '', int(o.lstrip('-')))
                for o in self.ordering.split('.')
            ]
        return []

    def get_order_by_clause(self):
        """
        Turn an ordering string like ``1.5.-3.-2.6`` into the respective SQL.

        SQL's column numbering starts at 1, so do we here. Given
        :attr:`self.ordering` as ``1.5.-3.-2.6`` return a string
        ``ORDER BY 1 ASC, 5 ASC, 3 DESC, 2 DESC, 6 ASC``.

        Ensures that each column (excluding the ``-`` prefix) is an integer by
        calling ``int()`` on it.
        """
        if self.parsed_ordering:
            ordering = [
                ('%d DESC' if direction == '-' else '%d ASC') % column
                for direction, column in self.parsed_ordering
            ]
            return 'ORDER BY ' + ', '.join(ordering)
        return ''


class CacheHitsMetric(Metric):
    """
    The typical rule for most applications is that only a fraction of its data
    is regularly accessed. As with many other things data can tend to follow
    the 80/20 rule with 20% of your data accounting for 80% of the reads and
    often times its higher than this. Postgres itself actually tracks access
    patterns of your data and will on its own keep frequently accessed data in
    cache. Generally you want your database to have a cache hit rate of about
    99%.

    (Source: http://www.craigkerstiens.com/2012/10/01/understanding-postgres-performance/)
    """
    label = _('Cache Hits')
    slug = 'cache-hits'
    sql = '''
        WITH cache AS (
            SELECT
                sum(heap_blks_read) heap_read,
                sum(heap_blks_hit) heap_hit,
                sum(heap_blks_hit) + sum(heap_blks_read) heap_sum
            FROM
                pg_statio_user_tables
        ) SELECT
            heap_read,
            heap_hit,
            CASE
                WHEN heap_sum = 0 THEN 'N/A'
                ELSE (heap_hit / heap_sum)::text
            END ratio
        FROM
            cache
        {ORDER_BY}
        ;
    '''


registry.register(CacheHitsMetric)


class IndexUsageMetric(Metric):
    """
    While there is no perfect answer, if you're not somewhere around 99% on any
    table over 10,000 rows you may want to consider adding an index. When
    examining where to add an index you should look at what kind of queries
    you're running. Generally you'll want to add indexes where you're looking
    up by some other id or on values that you're commonly filtering on such as
    created_at fields.

    (Source: http://www.craigkerstiens.com/2012/10/01/understanding-postgres-performance/)
    """
    label = _('Index Usage')
    ordering = '2'
    slug = 'index-usage'
    sql = '''
        SELECT
            relname,
            100 * idx_scan / (seq_scan + idx_scan) percent_of_times_index_used,
            n_live_tup rows_in_table
        FROM
            pg_stat_user_tables
        WHERE
            seq_scan + idx_scan > 0
        {ORDER_BY}
        ;
    '''


registry.register(IndexUsageMetric)


class AvailableExtensions(Metric):
    """
    PostgreSQL can be extended by installing extensions with the CREATE
    EXTENSION command. The list of available extensions on each database is
    shown below.
    """
    label = _('Available Extensions')
    ordering = '1'
    slug = 'available-extensions'
    sql = '''
        SELECT
            name,
            default_version,
            installed_version,
            comment
        FROM
            pg_available_extensions
        {ORDER_BY}
        ;
    '''


registry.register(AvailableExtensions)
