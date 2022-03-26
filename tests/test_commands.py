import io
from contextlib import contextmanager
from functools import partial
from unittest import mock

from django.conf import settings
from django.core.management import CommandError, call_command
from django.db import connection
from django.test import TestCase
from rich.console import Console

from postgres_metrics.metrics import (
    MetricResult,
    NoMetricResult,
    registry as metric_registry,
)


class RichConsoleMixin:
    @contextmanager
    def patch_console(self):
        with mock.patch(
            "django_rich.management.RichCommand.make_rich_console",
            partial(Console, width=200),
        ):
            yield


class TestListMetricsCommand(RichConsoleMixin, TestCase):
    def test_call(self):
        stdout = io.StringIO()
        with self.patch_console():
            call_command("pgm_list_metrics", stdout=stdout)
        out = stdout.getvalue()
        self.assertIn(" Slug ", out)
        self.assertIn(" Label ", out)
        self.assertIn(" Description ", out)
        for Metric in metric_registry:
            with self.subTest(metric=Metric):
                self.assertIn(str(Metric.label), out)
                self.assertIn(str(Metric.slug), out)


class TestShowMetricCommand(RichConsoleMixin, TestCase):
    databases = {name for name in settings.DATABASES if name != "sqlite"}

    def test_call_generic(self):
        for Metric in metric_registry:
            metric = Metric()
            metric.get_data()
            stdout = io.StringIO()
            with self.patch_console():
                call_command("pgm_show_metric", str(metric.slug), stdout=stdout)
            out = stdout.getvalue()
            for header in metric.headers:
                with self.subTest(metric=metric, header=header):
                    self.assertIn(str(header.name), out)

    def test_call_missing_metric(self):
        stdout = io.StringIO()
        with self.assertRaises(CommandError):
            with self.patch_console():
                call_command("pgm_show_metric", "[green]does-not-exist", stdout=stdout)
        out = stdout.getvalue()
        self.assertEqual("Metric '[green]does-not-exist' not found!\n", out)

    def test_call_no_data(self):
        stdout = io.StringIO()
        with mock.patch(
            "postgres_metrics.metrics.IndexSize.get_data",
            return_value=[
                MetricResult(connection, []),
                NoMetricResult(connection, "some reason"),
            ],
        ):
            with self.patch_console():
                call_command("pgm_show_metric", "index-size", stdout=stdout)
        out = stdout.getvalue()
        self.assertIn("\nsome reason\n", out)
