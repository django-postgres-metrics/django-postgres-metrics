import io
import os
from contextlib import contextmanager
from functools import partial
from unittest import mock

from django.conf import settings
from django.core.management import CommandError, call_command
from django.db import connection
from django.test import TestCase
from rich.console import Console

from postgres_metrics.management.commands import pgm_list_metrics, pgm_show_metric
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
            partial(Console, width=200, record=True),
        ):
            yield


class SaveSVGMixin:
    counter = 0

    def setUp(self):
        os.makedirs("tests/output/", exist_ok=True)

    def save_svg(self, cmd, name):
        cmd.console.save_svg(
            "tests/output/console-%02d-%s.svg" % (SaveSVGMixin.counter, name),
            title="django-postgres-metrics: %s" % name,
        )
        SaveSVGMixin.counter += 1


class TestListMetricsCommand(SaveSVGMixin, RichConsoleMixin, TestCase):
    def test_call(self):
        stdout = io.StringIO()
        with self.patch_console():
            cmd = pgm_list_metrics.Command()
            call_command(cmd, stdout=stdout)
            self.save_svg(cmd, "list")
        out = stdout.getvalue()
        self.assertIn(" Slug ", out)
        self.assertIn(" Label ", out)
        self.assertIn(" Description ", out)
        for Metric in metric_registry:
            with self.subTest(metric=Metric):
                self.assertIn(str(Metric.label), out)
                self.assertIn(str(Metric.slug), out)


class TestShowMetricCommand(SaveSVGMixin, RichConsoleMixin, TestCase):
    databases = {name for name in settings.DATABASES if name != "sqlite"}

    def test_call_generic(self):
        for Metric in metric_registry:
            metric = Metric()
            metric.get_data()
            stdout = io.StringIO()
            with self.patch_console():
                cmd = pgm_show_metric.Command()
                call_command(cmd, str(metric.slug), stdout=stdout)
                self.save_svg(cmd, metric.slug)
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
