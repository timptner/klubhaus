import logging

from accounts.models import User
from django.db import models
from django.utils import timezone
from klubhaus.mails import PostmarkTemplate

logger = logging.getLogger(__name__)


class Tournament(models.Model):
    title = models.CharField("Titel", max_length=250, unique=True)
    date = models.DateField("Datum")
    players = models.PositiveSmallIntegerField("Spieler")
    desc = models.TextField("Beschreibung", blank=True)
    registration_start = models.DateTimeField("Beginn der Einschreibung")
    registration_end = models.DateTimeField("Ende der Einschreibung")
    is_visible = models.BooleanField("Ist sichtbar?", default=True)

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

    def get_state(self):
        now = timezone.now()

        if now.date() > self.date:
            return 'Abgelaufen'

        if now > self.registration_end:
            return 'Geschlossen'

        if now < self.registration_start:
            return 'Geplant'

        return 'Geöffnet'

    def get_state_color(self):
        state = self.get_state()
        colors = {
            'Geplant': 'is-light is-info',
            'Geöffnet': 'is-light is-success',
            'Geschlossen': 'is-light is-danger',
            'Abgelaufen': 'is-light',
        }
        return colors[state]


class Team(models.Model):
    ENROLLED = 'E'
    APPROVED = 'A'
    REJECTED = 'R'
    STATE_CHOICES = [
        (ENROLLED, "Eingeschrieben"),
        (APPROVED, "Zugelassen"),
        (REJECTED, "Abgelehnt"),
    ]
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    captain = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField("Name", max_length=250)
    state = models.CharField("Status", max_length=1, choices=STATE_CHOICES, default=ENROLLED)
    created_at = models.DateTimeField("Erstellt am", auto_now_add=True)

    class Meta:
        verbose_name = "Team"
        verbose_name_plural = "Teams"
        ordering = ['created_at']
        constraints = [
            models.UniqueConstraint(fields=['tournament', 'captain'], name='unique_tournament_team'),
            models.UniqueConstraint(fields=['tournament', 'name'], name='unique_tournament_team_name'),
        ]
        permissions = [
            ('contact_team', "Can contact team captain"),
        ]

    def __str__(self):
        return self.name

    def get_state_color(self) -> str:
        colors = {
            self.ENROLLED: 'is-light is-info',
            self.APPROVED: 'is-light is-success',
            self.REJECTED: 'is-light is-danger',
        }
        try:
            color = colors[self.state]
        except KeyError:
            color = ''
        return color

    def set_state(self, state) -> bool:
        states = [choice for choice, label in self.STATE_CHOICES]
        if state not in states:
            choices = ', '.join(states)
            raise ValueError(f"You can only set a state to one of the available choices. ({choices})")

        self.state = state
        self.save()

        template = PostmarkTemplate()
        payload = {
            'captain_name': self.captain.first_name,
            'team_name': self.name,
            'tournament_name': self.tournament.title,
        }
        if state == self.APPROVED:
            error = template.send_message(self.captain.email, 'team-approved', payload)
        elif state == self.REJECTED:
            error = template.send_message(self.captain.email, 'team-rejected', payload)
        elif state == self.ENROLLED:
            raise NotImplementedError(f"Can not reset state to '{self.ENROLLED}'. Please request an administrator to "
                                      "use the available django-admin command.")
        else:
            error = None

        if error:
            logger.error("Failed to send email about changed state for team '%s'", self.name)
            return False

        return True


class Player(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    first_name = models.CharField("Vorname", max_length=50)
    last_name = models.CharField("Nachname", max_length=50)

    class Meta:
        verbose_name = "Spieler"
        verbose_name_plural = "Spieler"
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return self.get_full_name

    @property
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
