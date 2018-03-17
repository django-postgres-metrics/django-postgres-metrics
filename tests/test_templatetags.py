from django.template import Context, Template
from django.test import SimpleTestCase

from postgres_metrics.metrics import Metric


class RecordStyleTest(SimpleTestCase):

    def test(self):
        class MyMetric(Metric):
            sql = 'SELECT 1;'

            def get_record_style(self, record):
                return str(record)

        records = [
            ('',),
            '',
            ('abc', 123),
        ]
        expecteds = [
            'pgm-(&#39;&#39;,)',
            '',
            'pgm-(&#39;abc&#39;, 123)',
        ]

        t = Template(r'{% load postgres_metrics %}{% record_style %}')
        for record, expected in zip(records, expecteds):
            with self.subTest(records=record):
                output = t.render(Context({
                    'metric': MyMetric(),
                    'record': record,
                }))
                self.assertEqual(output, expected)


class RecordItemStyleTest(SimpleTestCase):

    def test(self):
        class MyMetric(Metric):
            sql = 'SELECT 1;'

            def get_record_item_style(self, record, item, index):
                if item:
                    return str((record, item, index))

        records = [
            ('', ''),
            ('a', ''),
            ('', 'b'),
            ('a', 4),
        ]
        expecteds = [
            ',,',
            'pgm-((&#39;a&#39;, &#39;&#39;), &#39;a&#39;, 0),,',
            ',pgm-((&#39;&#39;, &#39;b&#39;), &#39;b&#39;, 1),',
            'pgm-((&#39;a&#39;, 4), &#39;a&#39;, 0),pgm-((&#39;a&#39;, 4), 4, 1),',
        ]
        t = Template(r'{% load postgres_metrics %}{% for item in record %}{% record_item_style %},{% endfor %}')
        for record, expected in zip(records, expecteds):
            with self.subTest(records=record):
                output = t.render(Context({
                    'metric': MyMetric(),
                    'record': record,
                }))
                self.assertEqual(output, expected)
