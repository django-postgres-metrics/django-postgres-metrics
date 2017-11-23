from django.core.exceptions import ImproperlyConfigured
from django.db import connections
from django.test import SimpleTestCase, TestCase

from postgres_metrics.metrics import (
    Metric, MetricHeader, MetricRegistry, MetricResult, registry,
)


class MyMetric(Metric):
    label = 'My Metric'
    slug = 'my-new-metric'
    sql = 'SELECT 1 col1, 2 col2, 3 col3;'


class MetricRegistryTest(SimpleTestCase):

    def test_registry(self):
        registry.register(MyMetric)

        self.assertIn('my-new-metric', registry)
        self.assertIs(registry['my-new-metric'], MyMetric)

        registry.unregister('my-new-metric')

        self.assertNotIn('my-new-metric', registry)
        with self.assertRaises(KeyError):
            registry['my-new-metric']

        msg = 'Metric "MissingSQLMetric" is missing a "sql" attribute.'
        with self.assertRaisesMessage(ImproperlyConfigured, msg):
            class MissingSQLMetric(Metric):
                pass

        class MissingLabelAndSlugMetric(Metric):
            sql = 'SELECT 1;'

        self.assertEqual(MissingLabelAndSlugMetric.label, 'MissingLabelAndSlugMetric')
        self.assertEqual(MissingLabelAndSlugMetric.slug, 'missinglabelandslugmetric')

    def test_sorted(self):
        class FooBar(Metric):
            sql = 'SELECT 1;'

        class BarFoo(Metric):
            sql = 'SELECT 1;'

        class LoremIpsum(Metric):
            label = 'Lorem Ipsum'
            sql = 'SELECT 1;'

        registry = MetricRegistry()
        registry.register(FooBar)
        registry.register(BarFoo)
        registry.register(LoremIpsum)
        self.assertEqual(registry.sorted, [BarFoo, FooBar, LoremIpsum])


class MetricTest(TestCase):
    pass


class MetricHeaderTest(SimpleTestCase):

    def test_repr(self):
        header = MetricHeader('Some Name', 1, [])
        self.assertEqual(repr(header), '<MetricHeader "Some Name">')

    def test_str(self):
        header = MetricHeader('Some Name', 1, [])
        self.assertEqual(str(header), 'Some Name')

    def test_sort_priority(self):
        header = MetricHeader('H', 1, [])
        self.assertEqual(header.sort_priority, 0)
        header = MetricHeader('H', 4, [])
        self.assertEqual(header.sort_priority, 0)

        header = MetricHeader('H', 1, [('', 1)])
        self.assertEqual(header.sort_priority, 1)
        header = MetricHeader('H', 1, [('', 2), ('', 1)])
        self.assertEqual(header.sort_priority, 2)
        header = MetricHeader('H', 1, [('-', 2), ('', 3), ('-', 1), ('-', 9)])
        self.assertEqual(header.sort_priority, 3)

        header = MetricHeader('H', 4, [('', 4)])
        self.assertEqual(header.sort_priority, 1)
        header = MetricHeader('H', 4, [('', 2), ('', 4)])
        self.assertEqual(header.sort_priority, 2)
        header = MetricHeader('H', 4, [('-', 2), ('', 3), ('-', 4), ('-', 9)])
        self.assertEqual(header.sort_priority, 3)

    # Starting off from a non-existing sorting, make/remove/toggle the header
    # as a primary.
    def test_urls_from_empty_sorting_first_column_make_primary_url(self):
        header = MetricHeader('H', 1, [])
        self.assertEqual(header.url_primary, '1')

    def test_urls_from_empty_sorting_first_column_make_remove_url(self):
        header = MetricHeader('H', 1, [])
        self.assertEqual(header.url_remove, '')

    def test_urls_from_empty_sorting_first_column_make_toggle_url(self):
        header = MetricHeader('H', 1, [])
        self.assertEqual(header.url_toggle, '')

    def test_urls_from_empty_sorting_later_column_make_primary_url(self):
        header = MetricHeader('H', 4, [])
        self.assertEqual(header.url_primary, '4')

    def test_urls_from_empty_sorting_later_column_make_remove_url(self):
        header = MetricHeader('H', 4, [])
        self.assertEqual(header.url_remove, '')

    def test_urls_from_empty_sorting_later_column_make_toggle_url(self):
        header = MetricHeader('H', 4, [])
        self.assertEqual(header.url_toggle, '')

    # Starting off from primary sorting, make/remove/toggle the header
    # as a primary.
    def test_urls_from_primary_sorting_first_column_make_primary_url(self):
        header = MetricHeader('H', 1, [('', 1)])
        self.assertEqual(header.url_primary, '-1')

    def test_urls_from_primary_sorting_first_column_make_remove_url(self):
        header = MetricHeader('H', 1, [('', 1)])
        self.assertEqual(header.url_remove, '')

    def test_urls_from_primary_sorting_first_column_make_toggle_url(self):
        header = MetricHeader('H', 1, [('', 1)])
        self.assertEqual(header.url_toggle, '-1')

    def test_urls_from_primary_sorting_later_column_make_primary_url(self):
        header = MetricHeader('H', 4, [('', 4)])
        self.assertEqual(header.url_primary, '-4')

    def test_urls_from_primary_sorting_later_column_make_remove_url(self):
        header = MetricHeader('H', 4, [('', 4)])
        self.assertEqual(header.url_remove, '')

    def test_urls_from_primary_sorting_later_column_make_toggle_url(self):
        header = MetricHeader('H', 4, [('', 4)])
        self.assertEqual(header.url_toggle, '-4')

    # Starting off from descending primary sorting, make/remove/toggle the
    # header as a primary.
    def test_urls_from_desc_primary_sorting_first_column_make_primary_url(self):
        header = MetricHeader('H', 1, [('-', 1)])
        self.assertEqual(header.url_primary, '1')

    def test_urls_from_desc_primary_sorting_first_column_make_remove_url(self):
        header = MetricHeader('H', 1, [('-', 1)])
        self.assertEqual(header.url_remove, '')

    def test_urls_from_desc_primary_sorting_first_column_make_toggle_url(self):
        header = MetricHeader('H', 1, [('-', 1)])
        self.assertEqual(header.url_toggle, '1')

    def test_urls_from_desc_primary_sorting_later_column_make_primary_url(self):
        header = MetricHeader('H', 4, [('-', 4)])
        self.assertEqual(header.url_primary, '4')

    def test_urls_from_desc_primary_sorting_later_column_make_remove_url(self):
        header = MetricHeader('H', 4, [('-', 4)])
        self.assertEqual(header.url_remove, '')

    def test_urls_from_desc_primary_sorting_later_column_make_toggle_url(self):
        header = MetricHeader('H', 4, [('-', 4)])
        self.assertEqual(header.url_toggle, '4')

    # Starting off from non-primary sorting, make/remove/toggle the header
    def test_urls_from_non_primary_sorting_first_column_make_primary_url(self):
        header = MetricHeader('H', 1, [('-', 2), ('', 3), ('', 1)])
        self.assertEqual(header.url_primary, '-1.-2.3')

    def test_urls_from_non_primary_sorting_first_column_make_remove_url(self):
        header = MetricHeader('H', 1, [('-', 2), ('', 3), ('', 1)])
        self.assertEqual(header.url_remove, '-2.3')

    def test_urls_from_non_primary_sorting_first_column_make_toggle_url(self):
        header = MetricHeader('H', 1, [('-', 2), ('', 3), ('', 1)])
        self.assertEqual(header.url_toggle, '-2.3.-1')

    def test_urls_from_non_primary_sorting_later_column_make_primary_url(self):
        header = MetricHeader('H', 4, [('-', 2), ('', 3), ('', 4)])
        self.assertEqual(header.url_primary, '-4.-2.3')

    def test_urls_from_non_primary_sorting_later_column_make_remove_url(self):
        header = MetricHeader('H', 4, [('-', 2), ('', 3), ('', 4)])
        self.assertEqual(header.url_remove, '-2.3')

    def test_urls_from_non_primary_sorting_later_column_make_toggle_url(self):
        header = MetricHeader('H', 4, [('-', 2), ('', 3), ('', 4)])
        self.assertEqual(header.url_toggle, '-2.3.-4')

    # Starting off from descending non-primary sorting, make/remove/toggle the
    # header
    def test_urls_from_desc_non_primary_sorting_first_column_make_primary_url(self):
        header = MetricHeader('H', 1, [('-', 2), ('', 3), ('-', 1)])
        self.assertEqual(header.url_primary, '1.-2.3')

    def test_urls_from_desc_non_primary_sorting_first_column_make_remove_url(self):
        header = MetricHeader('H', 1, [('-', 2), ('', 3), ('-', 1)])
        self.assertEqual(header.url_remove, '-2.3')

    def test_urls_from_desc_non_primary_sorting_first_column_make_toggle_url(self):
        header = MetricHeader('H', 1, [('-', 2), ('', 3), ('-', 1)])
        self.assertEqual(header.url_toggle, '-2.3.1')

    def test_urls_from_desc_non_primary_sorting_later_column_make_primary_url(self):
        header = MetricHeader('H', 4, [('-', 2), ('', 3), ('-', 4)])
        self.assertEqual(header.url_primary, '4.-2.3')

    def test_urls_from_desc_non_primary_sorting_later_column_make_remove_url(self):
        header = MetricHeader('H', 4, [('-', 2), ('', 3), ('-', 4)])
        self.assertEqual(header.url_remove, '-2.3')

    def test_urls_from_desc_non_primary_sorting_later_column_make_toggle_url(self):
        header = MetricHeader('H', 4, [('-', 2), ('', 3), ('-', 4)])
        self.assertEqual(header.url_toggle, '-2.3.4')


class MetricResultTest(SimpleTestCase):

    def test(self):
        result = MetricResult(connections['default'], [('foo', 1, 2), ('bar', 3, 4)])
        self.assertEqual(result.alias, 'default')
        self.assertEqual(
            sorted(result.dsn.split()),
            sorted('user=someuser password=xxx dbname=test_somedb'.split()),
        )
        self.assertEqual(result.records, [('foo', 1, 2), ('bar', 3, 4)])

        result = MetricResult(connections['second'], [('foo', 1, 2), ('bar', 3, 4)])
        self.assertEqual(result.alias, 'second')
        self.assertEqual(
            sorted(result.dsn.split()),
            sorted('user=otheruser dbname=test_otherdb'.split()),
        )
        self.assertEqual(result.records, [('foo', 1, 2), ('bar', 3, 4)])
