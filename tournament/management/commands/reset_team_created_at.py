from accounts.models import User
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db.models import OuterRef, Subquery
from tournament.models import Team
from zoneinfo import ZoneInfo


class Command(BaseCommand):
    help = ("Set the created_at attribute for every team with the default date of 2023-01-01T00:00 to the date_joined "
            "attribute of the team captains user model")

    def handle(self, *args, **options):
        default_date = datetime(2023, 1, 1, tzinfo=ZoneInfo('Europe/Berlin'))
        queryset = Team.objects.filter(created_at=default_date)

        if not queryset.exists():
            self.stdout.write(
                self.style.WARNING("No teams found with default date of 2023-01-01T00:00")
            )
            return

        user = User.objects.filter(pk=OuterRef('pk'))
        updated = queryset.update(created_at=Subquery(user.values('date_joined')[:1]))

        self.stdout.write(
            self.style.SUCCESS(f"Successfully updated {updated} teams")
        )
