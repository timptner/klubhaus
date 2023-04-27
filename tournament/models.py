from accounts.models import User
from django.db import models
from django.utils import timezone


class Tournament(models.Model):
    title = models.CharField("Titel", max_length=250, unique=True)
    date = models.DateField("Datum")
    desc = models.TextField("Beschreibung", blank=True)
    registration_start = models.DateTimeField("Beginn der Einschreibung")
    registration_end = models.DateTimeField("Ende der Einschreibung")

    class Meta:
        verbose_name = "Turnier"
        verbose_name_plural = "Turniere"
        ordering = ['-date']
        constraints = [
            models.CheckConstraint(
                check=models.Q(registration_end__gt=models.F('registration_start')),
                name='registration_end_after_start',
            ),
            models.CheckConstraint(
                check=models.Q(registration_end__lt=models.F('date')),
                name='registration_end_before_date',
            ),
        ]

    def __str__(self):
        return self.title

    def get_status(self):
        now = timezone.now()

        if now.date() > self.date:
            return 'expired'

        if now > self.registration_end:
            return 'closed'

        if now < self.registration_start:
            return 'planned'

        return 'open'


class Team(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    captain = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField("Name", max_length=250)

    class Meta:
        verbose_name = "Team"
        verbose_name_plural = "Teams"
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['tournament', 'name'], name='unique_tournament_team'),
        ]

    def __str__(self):
        return self.name


class Player(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    first_name = models.CharField("Vorname", max_length=50)
    last_name = models.CharField("Nachname", max_length=50)

    class Meta:
        verbose_name = "Spieler"
        verbose_name_plural = "Spieler"
        ordering = ['first_name', 'last_name']
        constraints = [
            models.UniqueConstraint(fields=['team', 'first_name', 'last_name'], name='unique_team_player'),
        ]

    def __str__(self):
        return self.get_full_name

    @property
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
