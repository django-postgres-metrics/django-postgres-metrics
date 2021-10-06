import re

from django.core.exceptions import ImproperlyConfigured
from django.db import connections
from django.utils.encoding import force_str
from django.utils.functional import cached_property
from django.utils.html import escape, urlize
from django.utils.text import normalize_newlines, slugify
from django.utils.translation import gettext_lazy as _


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
        self.name = name.replace("-", " ").replace("_", " ")
        self.index = index
        self.ordering = ordering

    def __repr__(self):
        return '<MetricHeader "%s">' % self.name

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return (
            self.name == other.name
            and self.index == other.index
            and self.ordering == other.ordering
        )

    @staticmethod
    def join_ordering(ordering):
        return ".".join("%s%d" % o for o in ordering)

    @cached_property
    def ascending(self):
        """``True`` if the column is in ascending order ``False`` otherwise"""
        for index, (direction, column) in enumerate(self.ordering, start=1):
            if column == self.index and direction == "":
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
            [("-" if self.ascending else "", self.index)]
            + [
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
                direction if column != self.index else ("" if direction else "-"),
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

    holds_data = True

    def __init__(self, connection, records):
        connection.ensure_connection()
        self.alias = connection.alias
        self.dsn = connection.connection.dsn
        self.records = records


class NoMetricResult(MetricResult):
    """
    Internal class to pass an error message to the template when a metric is
    not available.
    """

    holds_data = False

    def __init__(self, connection, reason):
        super().__init__(connection, [])
        self.reason = reason


class MetricMeta(type):
    def __new__(mcs, name, bases, attrs):
        if bases:
            # Only subclasses of `Metric`
            if not attrs.get("label"):
                attrs["label"] = name
            if not attrs.get("slug"):
                attrs["slug"] = slugify(attrs["label"])
            if not attrs.get("sql"):
                msg = 'Metric "%s" is missing a "sql" attribute or "sql" is empty.'
                raise ImproperlyConfigured(msg % name)

            docstring = attrs.get("__doc__")
            if docstring and docstring.strip():
                docstring = normalize_newlines(force_str(docstring))
                docstring = "\n".join(line.strip() for line in docstring.split("\n"))
                paras = re.split("\n{2,}", docstring)
                paras = [
                    "<p>%s</p>" % urlize(escape(p).replace("\n", " ").strip())
                    for p in paras
                ]
                attrs["description"] = "\n\n".join(paras)
            else:
                attrs["description"] = ""

            attrs["permission_name"] = "can_view_metric_%s" % attrs["slug"].replace(
                "-", "_"
            )
            attrs["permission_key"] = "postgres_metrics.%s" % attrs["permission_name"]

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

    #: A list of strings used as column headers in the admin. Consider making
    #: the strings translateable. If the attribute is undefined, the column
    #: names returned by the database will be used.
    header_labels = None

    #: The label is what is used in the Django Admin views. Consider making
    #: this string translateable.
    label = ""

    #: The maximum PostgreSQL version possible to provide the metric data.
    #: If not explicitly specified, every PostgreSQL version is suitable. This
    # value is checked against
    # :attr:`django.db.backends.postgresql.base.DatabaseWrapper.pg_version`.
    max_pg_version = None

    #: The minimum PostgreSQL version necessary to provide the metric data.
    #: If not explicitly specified, every PostgreSQL version is suitable. This
    # value is checked against
    # :attr:`django.db.backends.postgresql.base.DatabaseWrapper.pg_version`.
    min_pg_version = None

    #: The default ordering that should be applied to the SQL query by default.
    #: This needs to be a valid ordering string as defined on
    #: :attr:`parsed_ordering`.
    ordering = ""

    #: A URL safe representation of the label and unique across all metrics.
    slug = ""

    #: The actual SQL statement that is being used to query the database. In
    #: order to make use of the :attr:`ordering`, include the string
    #: ``{ORDER_BY}`` in the query as necessary. For details on that value see
    #: :meth:`get_order_by_clause`.
    sql = ""

    def __init__(self, ordering=None):
        self.ordering = ordering or self.ordering

    def __repr__(self):
        return '<Metric "%s">' % self.label

    @classmethod
    def can_view(cls, user):
        """
        Check that the given a user instance has access to the metric.

        This requires the user instance to have the
        :attr:`django:django.contrib.auth.models.User.is_superuser` and
        :attr:`django:django.contrib.auth.models.User.is_staff` flags as
        well as the
        :meth:`django:django.contrib.auth.models.User.has_perm` method.

        Users with ``is_superuser=True`` will always have access to a metric.
        Users with ``is_staff=True`` will have access if and only if the user
        has the permission for a metric.
        """
        return user.is_superuser or user.is_staff and user.has_perm(cls.permission_key)

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
            if connection.vendor != "postgresql":
                continue
            if (
                self.min_pg_version is None
                or connection.pg_version >= self.min_pg_version
            ) and (
                self.max_pg_version is None
                or connection.pg_version <= self.max_pg_version
            ):
                with connection.cursor() as cursor:
                    cursor.execute(self.full_sql)
                    if self.header_labels is None:
                        self.header_labels = [c.name for c in cursor.description]
                    data = cursor.fetchall()
                db = MetricResult(connection, data)
            else:
                db = NoMetricResult(
                    connection,
                    "This metric is not supported on this PostgreSQL version.",
                )
            results.append(db)
        return results

    @cached_property
    def headers(self):
        """
        A wrapper around the :attr:`header_labels` to make the tables in the
        admin sortable.
        """
        return [
            MetricHeader(label, index, self.parsed_ordering)
            for index, label in enumerate(self.header_labels, start=1)
        ]

    @cached_property
    def parsed_ordering(self):
        """
        Turn an ordering string like ``1.5.-3.-2.6`` into the respective abstraction.

        Given :attr:`ordering` as ``1.5.-3.-2.6`` return a list of 2-tuples
        like ``[('', 1), ('', 5), ('-', 3), ('-', 2), ('', 6)]``.
        """
        if self.ordering:
            return [
                ("-" if o.startswith("-") else "", int(o.lstrip("-")))
                for o in self.ordering.split(".")
            ]
        return []

    def get_order_by_clause(self):
        """
        Turn an ordering string like ``1.5.-3.-2.6`` into the respective SQL.

        SQL's column numbering starts at 1, so do we here. Given
        :attr:`ordering` as ``1.5.-3.-2.6`` return a string
        ``ORDER BY 1 ASC, 5 ASC, 3 DESC, 2 DESC, 6 ASC``.

        Ensures that each column (excluding the ``-`` prefix) is an integer by
        calling ``int()`` on it.
        """
        if self.parsed_ordering:
            ordering = [
                ("%d DESC" if direction == "-" else "%d ASC") % column
                for direction, column in self.parsed_ordering
            ]
            return "ORDER BY " + ", ".join(ordering)
        return ""

    def get_record_style(self, record):
        """
        Given a single record from :class:`MetricResult`, decide how to style
        it. Most likely to be used with the template tag
        :func:`~postgres_metrics.templatetags.postgres_metrics.record_style`.

        By default, django-postgres-metrics supports for styling classes:

        * ``ok``
        * ``warning``
        * ``critical``
        * ``info``

        Override this method and return one of the above strings or ``None``
        to apply the given style to the entire record. In the Django Admin this
        will highlight the entire row.
        """
        return ""

    def get_record_item_style(self, record, item, index):
        """
        Given a single record from :class:`MetricResult`, the value of the
        current item within, and the current item's index, decide how to style
        it. Most likely to be used with the template tag
        :func:`~postgres_metrics.templatetags.postgres_metrics.record_item_style`.

        By default, django-postgres-metrics supports for styling classes:

        * ``ok``
        * ``warning``
        * ``critical``
        * ``info``

        Override this method and return one of the above strings or ``None``
        to apply the given style to the entire record. In the Django Admin this
        will highlight the entire row.
        """
        return ""


class CacheHits(Metric):
    """
    The typical rule for most applications is that only a fraction of its data
    is regularly accessed. As with many other things data can tend to follow
    the 80/20 rule with 20% of your data accounting for 80% of the reads and
    often times its higher than this. Postgres itself actually tracks access
    patterns of your data and will on its own keep frequently accessed data in
    cache. Generally you want your database to have a cache hit rate of about
    99%.

    (Source:
    http://www.craigkerstiens.com/2012/10/01/understanding-postgres-performance/)
    """

    header_labels = [_("Reads"), _("Hits"), _("Ratio")]
    label = _("Cache Hits")
    slug = "cache-hits"
    sql = """
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
    """

    def get_record_item_style(self, record, item, index):
        if index == 2 and item is not None and item != "N/A":
            ratio = float(item)
            if ratio < 0.95:
                return "critical"
            if ratio < 0.99:
                return "warning"
            return "ok"


registry.register(CacheHits)


class IndexSize(Metric):
    header_labels = [_("Table"), _("Index"), _("Size")]
    label = _("Index Size")
    ordering = "1.2"
    slugify = "index-size"
    sql = """
        SELECT
            relname,
            indexrelname,
            pg_size_pretty(index_size)
        FROM (
            SELECT
                relname,
                indexrelname,
                pg_relation_size(indexrelid) AS index_size
            FROM
                pg_stat_user_indexes
            {ORDER_BY}
        ) AS t
        ;
    """


registry.register(IndexSize)


class DetailedIndexUsage(Metric):
    """
    A metric similar to "Index Usage" but broken down by index.

    The "index scan over sequential scan" column shows how frequently an index
    was used in comparison to the total number of sequential and index scans on
    the table.

    Similarly, the "index scan on table" shows how often an index was used
    compared to the other indexes on the table.
    """

    header_labels = [
        _("Table"),
        _("Index"),
        _("Index Scan over Sequential Scan"),
        _("Index Scan on table"),
    ]
    label = _("Detailed Index Usage")
    ordering = "1.2"
    slug = "detailed-index-usage"
    sql = """
        SELECT
            t.relname,
            i.indexrelname,
            CASE t.seq_scan + t.idx_scan
                WHEN 0
                    THEN round(0.0, 2)
                ELSE
                    round(
                        (100::float * i.idx_scan / (t.seq_scan + t.idx_scan))::numeric,
                        2::int
                    )
            END,
            CASE t.idx_scan
                WHEN 0
                    THEN round(0.0, 2)
                ELSE
                    round((100::float * i.idx_scan / t.idx_scan)::numeric, 2::int)
            END
        FROM
            pg_stat_user_tables t
        INNER JOIN
            pg_stat_user_indexes i
            ON t.relid = i.relid
        {ORDER_BY}
        ;
    """


registry.register(DetailedIndexUsage)


class IndexUsage(Metric):
    """
    While there is no perfect answer, if you're not somewhere around 99% on any
    table over 10,000 rows you may want to consider adding an index. When
    examining where to add an index you should look at what kind of queries
    you're running. Generally you'll want to add indexes where you're looking
    up by some other id or on values that you're commonly filtering on such as
    created_at fields.

    (Source:
    http://www.craigkerstiens.com/2012/10/01/understanding-postgres-performance/)
    """

    header_labels = [_("Table"), _("Index used (in %)"), _("Num rows")]
    label = _("Index Usage")
    ordering = "2"
    slug = "index-usage"
    sql = """
        SELECT
            relname,
            round(
                (100::float * idx_scan / (seq_scan + idx_scan))::numeric,
                2::int
            ),
            n_live_tup
        FROM
            pg_stat_user_tables
        WHERE
            seq_scan + idx_scan > 0
        {ORDER_BY}
        ;
    """

    def get_record_style(self, record):
        if record[2]:
            usage = record[1]
            rowcount = record[2]
            if rowcount >= 10000:
                if usage < 95.00:
                    return "critical"
                if usage < 99.00:
                    return "warning"
                return "ok"


registry.register(IndexUsage)


class TableSize(Metric):
    """
    The "size" of a table in PostgreSQL can be different, depending on what to
    include when calculating "the size".

    The "Total size" for a relation is equal to the "Table size" plus all
    indexes.

    The "size of * fork" refers to the "main" data fork, the Free Space Map
    (fsm), Visibility Map (vm), and the initialization fork.

    See also the PostgreSQL documentation on the physical storage:
    https://www.postgresql.org/docs/current/storage.html
    """

    header_labels = [
        _("Table"),
        _("Total size"),
        _("Table size"),
        _("Size of 'main' fork"),
        _("Size of 'fsm' fork"),
        _("Size of 'vm' fork"),
        _("Size of 'init' fork"),
    ]
    label = _("Table Size")
    ordering = "1"
    slugify = "table-size"
    sql = """
        SELECT
            relname,
            pg_size_pretty(total_size),
            pg_size_pretty(table_size),
            pg_size_pretty(relation_size_main),
            pg_size_pretty(relation_size_fsm),
            pg_size_pretty(relation_size_vm),
            pg_size_pretty(relation_size_init)
        FROM (
            SELECT
                relname,
                pg_total_relation_size(relid) AS total_size,
                pg_table_size(relid) AS table_size,
                pg_relation_size(relid, 'main') AS relation_size_main,
                pg_relation_size(relid, 'fsm') AS relation_size_fsm,
                pg_relation_size(relid, 'vm') AS relation_size_vm,
                pg_relation_size(relid, 'init') AS relation_size_init
            FROM
                pg_stat_user_tables
            {ORDER_BY}
        ) AS t
        ;
    """


registry.register(TableSize)


class AvailableExtensions(Metric):
    """
    PostgreSQL can be extended by installing extensions with the CREATE
    EXTENSION command. The list of available extensions on each database is
    shown below.
    """

    label = _("Available Extensions")
    ordering = "1"
    slug = "available-extensions"
    sql = """
        SELECT
            name,
            default_version,
            installed_version,
            comment
        FROM
            pg_available_extensions
        {ORDER_BY}
        ;
    """

    def get_record_style(self, record):
        if record[2]:
            default_version = tuple(record[1].split("."))
            installed_version = tuple(record[2].split("."))
            if default_version == installed_version:
                return "ok"
            if default_version < installed_version:
                return "info"
            return "warning"


registry.register(AvailableExtensions)


class SequenceUsage(Metric):
    """
    Show the sequence usage within a PostgreSQL database. A usage over 75%
    will be marked as red, and a usage over 50% will be marked as yellow.
    """

    header_labels = [
        _("Table"),
        _("Column"),
        _("Sequence"),
        _("Last value"),
        _("Max value"),
        _("Used (in %)"),
    ]
    label = _("Sequence Usage")
    min_pg_version = 100000
    ordering = "-6.1.2.3"
    slug = "sequence-usage"
    sql = """
        SELECT
            tabcls.relname,
            attrib.attname,
            seqcls.relname,
            seq.last_value,
            seq.max_value,
            round(
                (
                    100::float * COALESCE(seq.last_value, 0)
                    / (seq.max_value - seq.start_value + 1)
                )::numeric,
                2::int
            )
        FROM
            pg_class AS seqcls
        INNER JOIN
            pg_sequences AS seq
            ON seqcls.relname = seq.sequencename
        INNER JOIN
            pg_depend AS dep
            ON seqcls.relfilenode = dep.objid
        INNER JOIN
            pg_class AS tabcls
            ON dep.refobjid = tabcls.relfilenode
        INNER JOIN
            pg_attribute AS attrib
            ON
                attrib.attnum = dep.refobjsubid
                AND attrib.attrelid = dep.refobjid
        WHERE
            seqcls.relkind = 'S'
        {ORDER_BY}
        ;
    """

    def get_record_style(self, record):
        usage = record[5]
        if usage >= 75.00:
            return "critical"
        if usage >= 50.00:
            return "warning"
        return "ok"


registry.register(SequenceUsage)
