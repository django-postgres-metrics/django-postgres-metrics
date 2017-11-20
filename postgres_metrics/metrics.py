from django.utils.functional import cached_property


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

    @property
    def description(self):
        return self.__doc__


class CacheHitsMetric(Metric):
    """
    The typical rule for most applications is that only a fraction of its data
    is regularly accessed. As with many other things data can tend to follow
    the 80/20 rule with 20% of your data accounting for 80% of the reads and
    often times its higher than this. Postgres itself actually tracks access
    patterns of your data and will on its own keep frequently accessed data in
    cache. Generally you want your database to have a cache hit rate of about
    99%.
    (<a href="http://www.craigkerstiens.com/2012/10/01/understanding-postgres-performance/">Source</a>)
    """
    label = 'Cache Hits'
    slug = 'cache-hits'
    sql = '''
        SELECT
            sum(heap_blks_read) heap_read,
            sum(heap_blks_hit)  heap_hit,
            sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) ratio
        FROM
            pg_statio_user_tables;
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
    (<a href="http://www.craigkerstiens.com/2012/10/01/understanding-postgres-performance/">Source</a>)
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
