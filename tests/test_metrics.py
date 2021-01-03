from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import connections
from django.test import SimpleTestCase, TestCase

from postgres_metrics.metrics import (
    AvailableExtensions,
    CacheHits,
    IndexUsage,
    Metric,
    MetricHeader,
    MetricRegistry,
    MetricResult,
    SequenceUsage,
    registry,
)


class MyMetric(Metric):
    label = "My Metric"
    slug = "my-new-metric"
    sql = "SELECT 1 col1, 2 col2, 3 col3;"


class MetricRegistryTest(SimpleTestCase):
    def test_registry(self):
        registry.register(MyMetric)

        self.assertIn("my-new-metric", registry)
        self.assertIs(registry["my-new-metric"], MyMetric)

        registry.unregister("my-new-metric")

        self.assertNotIn("my-new-metric", registry)
        with self.assertRaises(KeyError):
            registry["my-new-metric"]

    def test_sorted(self):
        class FooBar(Metric):
            sql = "SELECT 1;"

        class BarFoo(Metric):
            sql = "SELECT 1;"

        class LoremIpsum(Metric):
            label = "Lorem Ipsum"
            sql = "SELECT 1;"

        registry = MetricRegistry()
        registry.register(FooBar)
        registry.register(BarFoo)
        registry.register(LoremIpsum)
        self.assertEqual(registry.sorted, [BarFoo, FooBar, LoremIpsum])


class MetricTest(TestCase):
    databases = {name for name in settings.DATABASES if name != "sqlite"}

    def test_required_arguments(self):
        msg = (
            'Metric "MissingSQLMetric" is missing a "sql" attribute or "sql" is empty.'
        )
        with self.assertRaisesMessage(ImproperlyConfigured, msg):

            class MissingSQLMetric(Metric):
                pass

        msg = 'Metric "EmptySQLMetric" is missing a "sql" attribute or "sql" is empty.'
        with self.assertRaisesMessage(ImproperlyConfigured, msg):

            class EmptySQLMetric(Metric):
                sql = ""

        class MissingLabelAndSlugMetric(Metric):
            sql = "SELECT 1;"

        self.assertEqual(MissingLabelAndSlugMetric.label, "MissingLabelAndSlugMetric")
        self.assertEqual(MissingLabelAndSlugMetric.slug, "missinglabelandslugmetric")

    def test_description(self):
        class MyMetric(Metric):
            sql = "SELECT 1;"

        self.assertEqual(MyMetric.description, "")

        class MyEmptyDocstringMetric(Metric):
            """"""

            sql = "SELECT 1;"

        self.assertEqual(MyEmptyDocstringMetric.description, "")

        class MyDocumentedMetric(Metric):
            """
            Foo bar buz
            lorem ipsum

            New paragraph with https://an.url/to/something spanning
            multiple
            lines
            """

            sql = "SELECT 1;"

        expected = (
            "<p>Foo bar buz lorem ipsum</p>\n"
            "\n"
            '<p>New paragraph with <a href="https://an.url/to/something">'
            "https://an.url/to/something</a> spanning multiple lines</p>"
        )
        self.assertEqual(
            str(MyDocumentedMetric.description),
            expected,
        )

    def test_full_sql(self):
        class MyMetric(Metric):
            sql = "SELECT 1;"

        self.assertEqual(MyMetric().full_sql, "SELECT 1;")

        class OrderedMetric(Metric):
            ordering = "-2.1.3"
            sql = "SELECT 1 {ORDER_BY};"

        self.assertEqual(
            OrderedMetric().full_sql, "SELECT 1 ORDER BY 2 DESC, 1 ASC, 3 ASC;"
        )

    def test_get_data(self):
        class DjangoMigrationStatistics(Metric):
            """
            Count the number of applied Django migrations per app and sort by
            descending count and ascending app name.
            """

            label = "Migration Statistics"
            slug = "django-migration-statistics"
            ordering = "-2.1"
            sql = """
                SELECT
                    app, count(*)
                FROM
                    django_migrations
                GROUP BY
                    app
                {ORDER_BY}
                ;
            """

        metric = DjangoMigrationStatistics()
        data = metric.get_data()

        self.assertEqual(
            metric.headers,
            [
                MetricHeader("app", 1, [("-", 2), ("", 1)]),
                MetricHeader("count", 2, [("-", 2), ("", 1)]),
            ],
        )

        num_databases = len(settings.DATABASES) - 1  # One SQLite3 database
        self.assertEqual(len(data), num_databases)
        for i in range(num_databases):
            with self.subTest(db_number=i):
                # 4 apps
                self.assertEqual(len(data[i].records), 4)
                # 2 columns
                self.assertEqual(len(data[i].records[0]), 2)

    def test_get_record_style(self):
        class MyMetric(Metric):
            sql = "SELECT 1;"

        self.assertEqual(MyMetric().get_record_style(None), "")

    def test_get_record_item_style(self):
        class MyMetric(Metric):
            sql = "SELECT 1;"

        self.assertEqual(MyMetric().get_record_item_style(None, None, None), "")


class MetricHeaderTest(SimpleTestCase):
    def test_repr(self):
        header = MetricHeader("Some Name", 1, [])
        self.assertEqual(repr(header), '<MetricHeader "Some Name">')

    def test_str(self):
        header = MetricHeader("Some Name", 1, [])
        self.assertEqual(str(header), "Some Name")

    def test_sort_priority(self):
        header = MetricHeader("H", 1, [])
        self.assertEqual(header.sort_priority, 0)
        header = MetricHeader("H", 4, [])
        self.assertEqual(header.sort_priority, 0)

        header = MetricHeader("H", 1, [("", 1)])
        self.assertEqual(header.sort_priority, 1)
        header = MetricHeader("H", 1, [("", 2), ("", 1)])
        self.assertEqual(header.sort_priority, 2)
        header = MetricHeader("H", 1, [("-", 2), ("", 3), ("-", 1), ("-", 9)])
        self.assertEqual(header.sort_priority, 3)

        header = MetricHeader("H", 4, [("", 4)])
        self.assertEqual(header.sort_priority, 1)
        header = MetricHeader("H", 4, [("", 2), ("", 4)])
        self.assertEqual(header.sort_priority, 2)
        header = MetricHeader("H", 4, [("-", 2), ("", 3), ("-", 4), ("-", 9)])
        self.assertEqual(header.sort_priority, 3)

    # Starting off from a non-existing sorting, make/remove/toggle the header
    # as a primary.
    def test_urls_from_empty_sorting_first_column_make_primary_url(self):
        header = MetricHeader("H", 1, [])
        self.assertEqual(header.url_primary, "1")

    def test_urls_from_empty_sorting_first_column_make_remove_url(self):
        header = MetricHeader("H", 1, [])
        self.assertEqual(header.url_remove, "")

    def test_urls_from_empty_sorting_first_column_make_toggle_url(self):
        header = MetricHeader("H", 1, [])
        self.assertEqual(header.url_toggle, "")

    def test_urls_from_empty_sorting_later_column_make_primary_url(self):
        header = MetricHeader("H", 4, [])
        self.assertEqual(header.url_primary, "4")

    def test_urls_from_empty_sorting_later_column_make_remove_url(self):
        header = MetricHeader("H", 4, [])
        self.assertEqual(header.url_remove, "")

    def test_urls_from_empty_sorting_later_column_make_toggle_url(self):
        header = MetricHeader("H", 4, [])
        self.assertEqual(header.url_toggle, "")

    # Starting off from primary sorting, make/remove/toggle the header
    # as a primary.
    def test_urls_from_primary_sorting_first_column_make_primary_url(self):
        header = MetricHeader("H", 1, [("", 1)])
        self.assertEqual(header.url_primary, "-1")

    def test_urls_from_primary_sorting_first_column_make_remove_url(self):
        header = MetricHeader("H", 1, [("", 1)])
        self.assertEqual(header.url_remove, "")

    def test_urls_from_primary_sorting_first_column_make_toggle_url(self):
        header = MetricHeader("H", 1, [("", 1)])
        self.assertEqual(header.url_toggle, "-1")

    def test_urls_from_primary_sorting_later_column_make_primary_url(self):
        header = MetricHeader("H", 4, [("", 4)])
        self.assertEqual(header.url_primary, "-4")

    def test_urls_from_primary_sorting_later_column_make_remove_url(self):
        header = MetricHeader("H", 4, [("", 4)])
        self.assertEqual(header.url_remove, "")

    def test_urls_from_primary_sorting_later_column_make_toggle_url(self):
        header = MetricHeader("H", 4, [("", 4)])
        self.assertEqual(header.url_toggle, "-4")

    # Starting off from descending primary sorting, make/remove/toggle the
    # header as a primary.
    def test_urls_from_desc_primary_sorting_first_column_make_primary_url(self):
        header = MetricHeader("H", 1, [("-", 1)])
        self.assertEqual(header.url_primary, "1")

    def test_urls_from_desc_primary_sorting_first_column_make_remove_url(self):
        header = MetricHeader("H", 1, [("-", 1)])
        self.assertEqual(header.url_remove, "")

    def test_urls_from_desc_primary_sorting_first_column_make_toggle_url(self):
        header = MetricHeader("H", 1, [("-", 1)])
        self.assertEqual(header.url_toggle, "1")

    def test_urls_from_desc_primary_sorting_later_column_make_primary_url(self):
        header = MetricHeader("H", 4, [("-", 4)])
        self.assertEqual(header.url_primary, "4")

    def test_urls_from_desc_primary_sorting_later_column_make_remove_url(self):
        header = MetricHeader("H", 4, [("-", 4)])
        self.assertEqual(header.url_remove, "")

    def test_urls_from_desc_primary_sorting_later_column_make_toggle_url(self):
        header = MetricHeader("H", 4, [("-", 4)])
        self.assertEqual(header.url_toggle, "4")

    # Starting off from non-primary sorting, make/remove/toggle the header
    def test_urls_from_non_primary_sorting_first_column_make_primary_url(self):
        header = MetricHeader("H", 1, [("-", 2), ("", 3), ("", 1)])
        self.assertEqual(header.url_primary, "-1.-2.3")

    def test_urls_from_non_primary_sorting_first_column_make_remove_url(self):
        header = MetricHeader("H", 1, [("-", 2), ("", 3), ("", 1)])
        self.assertEqual(header.url_remove, "-2.3")

    def test_urls_from_non_primary_sorting_first_column_make_toggle_url(self):
        header = MetricHeader("H", 1, [("-", 2), ("", 3), ("", 1)])
        self.assertEqual(header.url_toggle, "-2.3.-1")

    def test_urls_from_non_primary_sorting_later_column_make_primary_url(self):
        header = MetricHeader("H", 4, [("-", 2), ("", 3), ("", 4)])
        self.assertEqual(header.url_primary, "-4.-2.3")

    def test_urls_from_non_primary_sorting_later_column_make_remove_url(self):
        header = MetricHeader("H", 4, [("-", 2), ("", 3), ("", 4)])
        self.assertEqual(header.url_remove, "-2.3")

    def test_urls_from_non_primary_sorting_later_column_make_toggle_url(self):
        header = MetricHeader("H", 4, [("-", 2), ("", 3), ("", 4)])
        self.assertEqual(header.url_toggle, "-2.3.-4")

    # Starting off from descending non-primary sorting, make/remove/toggle the
    # header
    def test_urls_from_desc_non_primary_sorting_first_column_make_primary_url(self):
        header = MetricHeader("H", 1, [("-", 2), ("", 3), ("-", 1)])
        self.assertEqual(header.url_primary, "1.-2.3")

    def test_urls_from_desc_non_primary_sorting_first_column_make_remove_url(self):
        header = MetricHeader("H", 1, [("-", 2), ("", 3), ("-", 1)])
        self.assertEqual(header.url_remove, "-2.3")

    def test_urls_from_desc_non_primary_sorting_first_column_make_toggle_url(self):
        header = MetricHeader("H", 1, [("-", 2), ("", 3), ("-", 1)])
        self.assertEqual(header.url_toggle, "-2.3.1")

    def test_urls_from_desc_non_primary_sorting_later_column_make_primary_url(self):
        header = MetricHeader("H", 4, [("-", 2), ("", 3), ("-", 4)])
        self.assertEqual(header.url_primary, "4.-2.3")

    def test_urls_from_desc_non_primary_sorting_later_column_make_remove_url(self):
        header = MetricHeader("H", 4, [("-", 2), ("", 3), ("-", 4)])
        self.assertEqual(header.url_remove, "-2.3")

    def test_urls_from_desc_non_primary_sorting_later_column_make_toggle_url(self):
        header = MetricHeader("H", 4, [("-", 2), ("", 3), ("-", 4)])
        self.assertEqual(header.url_toggle, "-2.3.4")


class MetricResultTest(TestCase):
    databases = {name for name in settings.DATABASES if name != "sqlite"}

    def test_db(self):
        for dbname, dbcfg in settings.DATABASES.items():
            if dbname == "sqlite":
                continue

            with self.subTest(dbname=dbname):
                result = MetricResult(
                    connections[dbname], [("foo", 1, 2), ("bar", 3, 4)]
                )
                self.assertEqual(result.alias, dbname)
                self.assertEqual(
                    sorted(result.dsn.split()),
                    sorted(
                        (
                            "host=localhost port=%d user=%s password=xxx dbname=%s"
                            % (dbcfg["PORT"], dbcfg["USER"], dbcfg["NAME"])
                        ).split()
                    ),
                )
                self.assertEqual(result.records, [("foo", 1, 2), ("bar", 3, 4)])


class StyleAssertionMixin:
    def assertRecordStylesEqual(self, metric_class, records, expecteds):
        metric = metric_class()
        for record, expected in zip(records, expecteds):
            with self.subTest(record=record):
                style = metric.get_record_style(record)
                self.assertEqual(style, expected)

    def assertRecordItemStylesEqual(self, metric_class, records, expecteds):
        metric = metric_class()
        for record, expected in zip(records, expecteds):
            with self.subTest(record=record):
                styles = tuple(
                    metric.get_record_item_style(record, item, index)
                    for index, item in enumerate(record)
                )
                self.assertEqual(styles, expected)


class AvailableExtensionsTest(StyleAssertionMixin, SimpleTestCase):
    def test_get_record_style(self):
        records = [
            ("ltree", "1.0", None, "bla"),
            ("ltree", "1.0", "0.0", "bla"),
            ("ltree", "4.0", "4.0", "bla"),
            ("ltree", "5.0", "5.0.1", "bla"),
        ]
        expecteds = [
            None,
            "warning",
            "ok",
            "info",
        ]
        self.assertRecordStylesEqual(AvailableExtensions, records, expecteds)


class CacheHitsTest(StyleAssertionMixin, SimpleTestCase):
    def test_get_record_item_style(self):
        records = [
            (123, 456, "N/A"),
            (123, 456, "0.94449"),
            (123, 456, "0.95"),
            (123, 456, "0.98999"),
            (123, 456, "0.99"),
        ]
        expecteds = [
            (None, None, None),
            (None, None, "critical"),
            (None, None, "warning"),
            (None, None, "warning"),
            (None, None, "ok"),
        ]
        self.assertRecordItemStylesEqual(CacheHits, records, expecteds)


class IndexUsageTest(StyleAssertionMixin, SimpleTestCase):
    def test_get_record_style(self):
        records = [
            ("table1", 12.34, 0),
            ("table1", 12.34, 9999),
            ("table1", 94.99, 10000),
            ("table1", 95.00, 10000),
            ("table1", 98.99, 10000),
            ("table1", 99.00, 10000),
        ]
        expecteds = [
            None,
            None,
            "critical",
            "warning",
            "warning",
            "ok",
        ]
        self.assertRecordStylesEqual(IndexUsage, records, expecteds)


class SequenceUsageTest(StyleAssertionMixin, SimpleTestCase):
    def test_get_record_style(self):
        records = [
            ("table1", "id", "table1_id_seq", None, 10000, 0.00),
            ("table1", "id", "table1_id_seq", 4999, 10000, 49.99),
            ("table1", "id", "table1_id_seq", 5000, 10000, 50.00),
            ("table1", "id", "table1_id_seq", 7499, 10000, 74.99),
            ("table1", "id", "table1_id_seq", 7500, 10000, 75.00),
        ]
        expecteds = [
            "ok",
            "ok",
            "warning",
            "warning",
            "critical",
        ]
        self.assertRecordStylesEqual(SequenceUsage, records, expecteds)


def gen_metric_test_case(metric_class):
    def test_get_data_default_ordering(self):
        metric = self.metric_class()
        metric.get_data()

    def test_get_data_no_ordering(self):
        metric = self.metric_class()
        metric.ordering = ""
        metric.get_data()

    def test_get_data_explicit_ordering(self):
        metric = self.metric_class(ordering="1.-2")
        metric.get_data()

    def test_repr(self):
        self.assertEqual(
            repr(self.metric_class()), '<Metric "%s">' % self.metric_class.label
        )

    tc_name = "Dynamic_" + metric_class.__name__ + "Test"
    attrs = {
        "databases": {name for name in settings.DATABASES if name != "sqlite"},
        "metric_class": metric_class,
        "test_get_data_default_ordering": test_get_data_default_ordering,
        "test_get_data_no_ordering": test_get_data_no_ordering,
        "test_get_data_explicit_ordering": test_get_data_explicit_ordering,
        "test_repr": test_repr,
    }
    cls = type(tc_name, (TestCase,), attrs)
    return tc_name, cls


for metric_class in registry:
    tc_name, tc = gen_metric_test_case(metric_class)
    locals()[tc_name] = tc
