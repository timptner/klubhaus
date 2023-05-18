from django.core.management.base import BaseCommand, CommandError

from tournament.models import Tournament


class Command(BaseCommand):
    help = "Delete the specified tournament"

    def add_arguments(self, parser):
        parser.add_argument('tournament_id', type=int)

    def handle(self, *args, **options):
        pk = options['tournament_id']
        try:
            tournament = Tournament.objects.get(pk=pk)
        except Tournament.DoesNotExist:
            raise CommandError(f"Tournament {pk} does not exist")

        tournament.delete()

        self.stdout.write(
            self.style.SUCCESS(f"Successfully deleted tournament {pk}")
        )
