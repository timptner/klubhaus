from django.core.management.base import BaseCommand, CommandError

from tournament.models import Team


class Command(BaseCommand):
    help = "Delete the specified team"

    def add_arguments(self, parser):
        parser.add_argument('team_id', type=int)

    def handle(self, *args, **options):
        pk = options['team_id']
        try:
            team = Team.objects.get(pk=pk)
        except Team.DoesNotExist:
            raise CommandError(f"Team {pk} does not exist")

        team.delete()

        self.stdout.write(
            self.style.SUCCESS(f"Successfully deleted team {pk}")
        )
