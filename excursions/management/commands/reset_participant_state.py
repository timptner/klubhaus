from django.core.management.base import BaseCommand, CommandError

from accounts.models import User
from excursions.models import Excursion, Participant


class Command(BaseCommand):
    help = "Set state of participant set for specified excursion to enrolled"

    def add_arguments(self, parser):
        parser.add_argument('excursion_id', type=int)

    def handle(self, *args, **options):
        excursion_id = options['excursion_id']

        try:
            excursion = Excursion.objects.get(pk=excursion_id)
        except Excursion.DoesNotExist:
            raise CommandError(f"Excursion \"{excursion_id}\" does not exist")

        updated = excursion.participant_set.update(state=Participant.ENROLLED)

        self.stdout.write(
            self.style.SUCCESS(f"Successfully changed state of {updated} participants to enrolled")
        )
