import django
from django.contrib.auth.models import AnonymousUser, Permission, User
from django.template import Context, Template
from django.test import RequestFactory, SimpleTestCase, TestCase

from postgres_metrics.metrics import Metric


class GetPostgresMetricsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("user", "user@local")
        cls.superuser = User.objects.create_superuser(
            "superuser", "superuser@local", "secret"
        )
        cls.staff_denied = User.objects.create_user(
            "staff_denied", "staff_denied@local", is_staff=True
        )
        cls.staff_permitted = User.objects.create_user(
            "staff_permitted", "staff_permitted@local", is_staff=True
        )
        cls.staff_permitted.user_permissions.add(
            Permission.objects.get(codename="can_view_metric_cache_hits")
        )

    def test(self):
        t = Template(
            r"{% load postgres_metrics %}{% get_postgres_metrics as postgres_metrics %}"
            r"{% for iter_metric in postgres_metrics %}"
            r"{{ iter_metric.slug }} "
            r"{% endfor %}",
        )
        data = [
            (AnonymousUser(), ""),
            (self.user, ""),
            (self.staff_denied, ""),
            (self.staff_permitted, "cache-hits "),
            (
                self.superuser,
                "available-extensions cache-hits detailed-index-usage index-size index-"
                "usage sequence-usage table-size ",
            ),
        ]
        rf = RequestFactory()
        for user, expected in data:
            with self.subTest(user=user):
                request = rf.get("/")
                request.user = user
                output = t.render(
                    Context(
                        {
                            "request": request,
                        }
                    )
                )
                self.assertEqual(output, expected)


class RecordStyleTest(SimpleTestCase):
    def test(self):
        class MyMetric(Metric):
            sql = "SELECT 1;"

            def get_record_style(self, record):
                return str(record)

        records = [
            ("",),
            "",
            ("abc", 123),
        ]
        if django.VERSION[:2] >= (3, 0):
            expecteds = [
                "pgm-(&#x27;&#x27;,)",
                "",
                "pgm-(&#x27;abc&#x27;, 123)",
            ]
        else:
            expecteds = [
                "pgm-(&#39;&#39;,)",
                "",
                "pgm-(&#39;abc&#39;, 123)",
            ]

        t = Template(r"{% load postgres_metrics %}{% record_style %}")
        for record, expected in zip(records, expecteds):
            with self.subTest(records=record):
                output = t.render(
                    Context(
                        {
                            "metric": MyMetric(),
                            "record": record,
                        }
                    )
                )
                self.assertEqual(output, expected)


class RecordItemStyleTest(SimpleTestCase):
    def test(self):
        class MyMetric(Metric):
            sql = "SELECT 1;"

            def get_record_item_style(self, record, item, index):
                if item:
                    return str((record, item, index))

        records = [
            ("", ""),
            ("a", ""),
            ("", "b"),
            ("a", 4),
        ]
        if django.VERSION[:2] >= (3, 0):
            expecteds = [
                ",,",
                "pgm-((&#x27;a&#x27;, &#x27;&#x27;), &#x27;a&#x27;, 0),,",
                ",pgm-((&#x27;&#x27;, &#x27;b&#x27;), &#x27;b&#x27;, 1),",
                "pgm-((&#x27;a&#x27;, 4), &#x27;a&#x27;, 0),pgm-((&#x27;a&#x27;, 4), 4, 1),",  # noqa
            ]
        else:
            expecteds = [
                ",,",
                "pgm-((&#39;a&#39;, &#39;&#39;), &#39;a&#39;, 0),,",
                ",pgm-((&#39;&#39;, &#39;b&#39;), &#39;b&#39;, 1),",
                "pgm-((&#39;a&#39;, 4), &#39;a&#39;, 0),pgm-((&#39;a&#39;, 4), 4, 1),",
            ]
        t = Template(
            r"{% load postgres_metrics %}{% for item in record %}"
            r"{% record_item_style %},{% endfor %}"
        )
        for record, expected in zip(records, expecteds):
            with self.subTest(records=record):
                output = t.render(
                    Context(
                        {
                            "metric": MyMetric(),
                            "record": record,
                        }
                    )
                )
                self.assertEqual(output, expected)
