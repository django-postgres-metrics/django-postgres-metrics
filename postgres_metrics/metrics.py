import re

from django.db import connections
from django.utils.encoding import force_text
from django.utils.functional import cached_property
from django.utils.html import escape, urlize
from django.utils.text import normalize_newlines


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
        self._registry[metric.slug] = metric

    @cached_property
    def sorted(self):
        return sorted((m for m in self), key=lambda m: m.label)


registry = MetricRegistry()


def join_ordering(ordering):
    return '.'.join('%s%d' % o for o in ordering)


class Header:

    def __init__(self, name, index, ordering):
        self.name = name.replace('-', ' ')
        self.index = index
        self.ordering = ordering

    def __repr__(self):
        return '<Header "%s">' % self.name

    def __str__(self):
        return self.name

    @cached_property
    def ascending(self):
        for index, (direction, column) in enumerate(self.ordering, start=1):
            if column == self.index and direction == '':
                return True
        return False

    @cached_property
    def sort_priority(self):
        for index, (direction, column) in enumerate(self.ordering, start=1):
            if column == self.index:
                return index
        return 0

    @cached_property
    def url_primary(self):
        return join_ordering(
            [('-' if self.ascending else '', self.index)] +
            [
                (direction, column)
                for direction, column in self.ordering
                if column != self.index
            ],
        )

    @cached_property
    def url_remove(self):
        return join_ordering(
            (direction, column)
            for direction, column in self.ordering
            if column != self.index
        )

    @cached_property
    def url_toggle(self):
        return join_ordering(
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

    def __init__(self, connection, metric):
        self._connection = connection
        self._get_data(metric)

    @property
    def alias(self):
        return self._connection.alias

    @property
    def dsn(self):
        return self._connection.connection.dsn

    def _get_data(self, metric):
        sql = metric.full_sql
        with self._connection.cursor() as cursor:
            cursor.execute(sql)
            self.headers = [
                Header(c.name, index, metric.parsed_ordering)
                for index, c in enumerate(cursor.description, start=1)
            ]
            self.records = cursor.fetchall()


class Metric:
    label = ''
    ordering = ''
    slug = ''
    sql = ''

    def __init__(self, ordering=None):
        self.ordering = ordering or self.ordering

    @cached_property
    def description(self):
        value = normalize_newlines(force_text(self.__doc__))
        paras = re.split('\n{2,}', value)
        paras = [
            '<p>%s</p>' % urlize(escape(p).replace('\n', ' '))
            for p in paras
        ]
        return '\n\n'.join(paras)

    @property
    def full_sql(self):
        return self.sql.format(ORDER_BY=self.get_order_by_clause())

    def get_data(self):
        results = []
        for connection in connections.all():
            if connection.vendor != 'postgresql':
                continue
            db = MetricResult(connection, self)
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
    label = 'Cache Hits'
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
    label = 'Index Usage'
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
    label = 'Available Extensions'
    # ordering = '1'
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
