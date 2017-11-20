import re

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


class Metric:
    label = ''
    slug = ''
    sql = ''

    @cached_property
    def description(self):
        value = normalize_newlines(force_text(self.__doc__))
        paras = re.split('\n{2,}', value)
        paras = [
            '<p>%s</p>' % urlize(escape(p).replace('\n', ' '))
            for p in paras
        ]
        return '\n\n'.join(paras)


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
        ORDER BY
            percent_of_times_index_used DESC;
    '''


registry.register(IndexUsageMetric)
