from django.core.management.base import BaseCommand, CommandError

from accounts.models import User
from excursions.models import Excursion, Participant


class Command(BaseCommand):
    help = "Deletes the participant specified via excursion and user"

    def add_arguments(self, parser):
        parser.add_argument('excursion_id', type=int)
        parser.add_argument('user_id', type=int)

    def handle(self, *args, **options):
        excursion_id = options['excursion_id']

        try:
            excursion = Excursion.objects.get(pk=excursion_id)
        except Excursion.DoesNotExist:
            raise CommandError(f"Excursion \"{excursion_id}\" does not exist")

        user_id = options['user_id']

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise CommandError(f"User \"{user_id}\" does not exist")

        try:
            participant = Participant.objects.filter(excursion=excursion, user=user).get()
        except Participant.DoesNotExist:
            raise CommandError(f"{user.get_full_name()} is not a participant of {excursion}")

        participant.delete()

        self.stdout.write(
            self.style.SUCCESS(f"Successfully removed {user.get_full_name()} as participant of {excursion}")
        )
