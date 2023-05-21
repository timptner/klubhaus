from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from excursions.reports import ParticipantList
from excursions.models import Excursion


class Command(BaseCommand):
    help = "Generate participant list for specified excursion as pdf report"

    def add_arguments(self, parser):
        parser.add_argument('excursion_id', type=int)

    def handle(self, *args, **options):
        excursion_id = options['excursion_id']

        try:
            excursion = Excursion.objects.get(pk=excursion_id)
        except Excursion.DoesNotExist:
            raise CommandError(f"Excursion \"{excursion_id}\" does not exist")

        file: Path = settings.MEDIA_ROOT / 'excursions' / 'reports' / 'Teilnehmerliste.pdf'

        if not file.parent.exists():
            file.parent.mkdir(parents=True)
            self.stdout.write("Created missing parent folders")

        report = ParticipantList(excursion=excursion)
        report.generate_pdf(str(file))

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created pdf report for {excursion.title} at {file}")
        )
