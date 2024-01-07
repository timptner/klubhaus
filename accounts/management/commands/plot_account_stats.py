import matplotlib.pyplot as plt

from datetime import date, timedelta
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db.models import DateField, Count
from django.db.models.functions import Cast

from accounts.models import User


class Command(BaseCommand):
    help = "Generate new SVG image for user accounts statistic"

    def add_arguments(self, parser):
        parser.add_argument('days', nargs='?', type=int, default=30)

    def handle(self, *args, **options):
        days = options['days']
        today = date.today()
        first_date = today - timedelta(days=days)
        queryset = User.objects.filter(
            date_joined__date__gte=first_date,
        ).values(
            'date_joined__date',
        ).annotate(count=Count('id'))

        data = {item['date_joined__date']: item['count'] for item in queryset}

        for n in range(days):
            current_date = first_date + timedelta(days=n + 1)
            if current_date not in data.keys():
                data[current_date] = 0

        dates, counts = zip(*data.items())

        output_dir = Path(settings.MEDIA_ROOT) / 'statistics' / 'accounts'
        if not output_dir.exists():
            output_dir.mkdir(parents=True)

        file_name = output_dir / f'{today.isoformat()}_history.svg'

        fig, ax = plt.subplots(figsize=(9, 3), dpi=80, layout='constrained')
        ax.bar(dates, counts)
        ax.set_ylim(0, max(*data.values(), 5))
        for label in ax.get_xticklabels():
            label.set_rotation(40)
            label.set_horizontalalignment('right')
        ax.set_title(f'{min(dates)} bis {max(dates)}')

        fig.savefig(file_name, transparent=True)

        self.stdout.write(
            self.style.SUCCESS(f"New graph generated: {file_name}")
        )
