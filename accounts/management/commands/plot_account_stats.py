import matplotlib.pyplot as plt

from datetime import date, timedelta
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db.models import Count

from accounts.models import User


class Command(BaseCommand):
    help = "Generate new SVG image for user accounts statistic"

    def add_arguments(self, parser):
        end = date.today()
        start = end - timedelta(days=30)
        parser.add_argument('start', nargs='?', type=date.fromisoformat, default=start)
        parser.add_argument('end', nargs='?', type=date.fromisoformat, default=end)

    def handle(self, *args, **options):
        start = options['start']
        end = options['end']

        if start >= end:
            raise CommandError("Start date must be earlier than end date")

        queryset = User.objects.filter(
            date_joined__date__gte=start,
            date_joined__date__lte=end,
        ).values(
            'date_joined__date',
        ).annotate(count=Count('id'))

        data = {item['date_joined__date']: item['count'] for item in queryset}

        current = start
        while current <= end:
            if current not in data.keys():
                data[current] = 0
            current = current + timedelta(days=1)

        dates, counts = zip(*data.items())

        output_dir = Path(settings.MEDIA_ROOT) / 'statistics' / 'accounts'
        if not output_dir.exists():
            output_dir.mkdir(parents=True)

        file_name = output_dir / f'{start.isoformat()}_{end.isoformat()}.svg'

        fig, ax = plt.subplots(figsize=(9, 3), dpi=80, layout='constrained')
        ax.set_axisbelow(True)
        ax.grid(axis='y')
        ax.bar(dates, counts)
        ax.set_ylim(0, max(*data.values(), 4) + 1)
        for label in ax.get_xticklabels():
            label.set_rotation(40)
            label.set_horizontalalignment('right')
        ax.set_title(f'{min(dates)} bis {max(dates)}')

        fig.savefig(file_name, transparent=True)

        self.stdout.write(
            self.style.SUCCESS(f"New graph generated: {file_name}")
        )
