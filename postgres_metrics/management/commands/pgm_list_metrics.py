import textwrap

from django_rich.management import RichCommand
from rich.markup import escape
from rich.table import Table

from postgres_metrics.metrics import registry as metrics_registry


class Command(RichCommand):
    def handle(self, *args, **options):
        table = Table()
        table.add_column("Slug", no_wrap=True)
        table.add_column("Label", no_wrap=True)
        table.add_column("Description")
        for metric in metrics_registry.sorted:
            description = metric.__doc__ or ""
            table.add_row(
                escape(str(metric.slug)),
                escape(str(metric.label)),
                escape(textwrap.dedent(description).strip()),
            )
        self.console.print(table)
