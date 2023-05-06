from django.core.management.base import BaseCommand
from tournament.models import Tournament, Team


class Command(BaseCommand):
    help = f"Set state for all teams of a tournament to '{Team.ENROLLED}'"

    def add_arguments(self, parser):
        parser.add_argument('tournament_pk', type=int)

    def handle(self, *args, **options):
        tournament = Tournament.objects.get(pk=options['tournament_pk'])
        amount = tournament.team_set.update(state=Team.ENROLLED)

        self.stdout.write(
            self.style.SUCCESS(f"Successfully updated {amount} teams")
        )
