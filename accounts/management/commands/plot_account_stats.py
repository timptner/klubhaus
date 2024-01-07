import matplotlib.pyplot as plt

from datetime import datetime, timedelta
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from accounts.models import User


class Command(BaseCommand):
    help = "Generate new SVG image for user accounts statistic"

    def add_arguments(self, parser):
        parser.add_argument('days', nargs='?', type=int, default=30)

    def handle(self, *args, **options):
        days = options['days']
        today = datetime.utcnow().date()
        data = {today - timedelta(days=n): 0 for n in range(days, 0, -1)}
        users = User.objects.filter(date_joined__gt=min(data.keys()))

        for user in users:
            date = user.date_joined.date()
            data[date] += 1

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
