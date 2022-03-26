from django.core.management import CommandError
from django_rich.management import RichCommand
from rich.markup import escape
from rich.table import Table
from rich.text import Text

from postgres_metrics.metrics import registry as metrics_registry

RICH_STYLE_MAPPING = {
    "ok": "green",
    "warning": "yellow",
    "critical": "red",
    "info": "blue",
}


class Command(RichCommand):
    def add_arguments(self, parser):
        """
        Entry point for subclassed commands to add custom arguments.
        """
        parser.add_argument("metric", help="The metric's slug")

    def handle(self, *args, **options):
        name = options["metric"]
        try:
            metric = metrics_registry[name]()
        except KeyError:
            self.console.print(Text(f"Metric '{name}' not found!", style="bold red"))
            raise CommandError(1)

        results = metric.get_data()
        for result in results:
            if result.holds_data:
                table = Table(
                    title=f"{escape(result.alias)} ({escape(result.dsn)})",
                    title_style="bold green",
                )
                for header in metric.headers:
                    table.add_column(escape(header.name), no_wrap=True)
                for record in result.records:
                    table.add_row(
                        *[
                            Text(
                                str(item),
                                style=RICH_STYLE_MAPPING.get(
                                    metric.get_record_item_style(record, item, idx)
                                ),
                            )
                            for idx, item in enumerate(record)
                        ],
                        style=RICH_STYLE_MAPPING.get(metric.get_record_style(record)),
                    )
                self.console.print(table)
            else:
                self.console.print(escape(result.reason), style="bold red")
