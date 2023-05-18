from django.core.management.base import BaseCommand, CommandError

from excursions.models import Excursion


class Command(BaseCommand):
    help = "Deletes the specified excursion"

    def add_arguments(self, parser):
        parser.add_argument('excursion_id', type=int)

    def handle(self, *args, **options):
        excursion_id = options['excursion_id']

        try:
            excursion = Excursion.objects.get(pk=excursion_id)
        except Excursion.DoesNotExist:
            raise CommandError(f"Excursion \"{excursion_id}\" does not exist")

        excursion.delete()

        self.stdout.write(
            self.style.SUCCESS(f"Successfully deleted excursion \"{excursion_id}\"")
        )
