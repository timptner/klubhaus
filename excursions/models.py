import logging

from django.db import models
from django.db.models import Q

from accounts.models import User
from klubhaus.mails import PostmarkTemplate


logger = logging.getLogger(__name__)


def image_path():
    pass


class Excursion(models.Model):
    PLANNED = 0
    OPENED = 1
    CLOSED = 2
    ARCHIVED = 3
    STATE_CHOICES = [
        (PLANNED, "Geplant"),
        (OPENED, "Geöffnet"),
        (CLOSED, "Geschlossen"),
        (ARCHIVED, "Archiviert"),
    ]
    title = models.CharField("Titel", max_length=200)
    location = models.CharField("Standort", max_length=200, blank=True)
    desc = models.TextField("Beschreibung")
    date = models.DateField("Datum")
    image = models.ImageField("Bild", blank=True, null=True)
    website = models.URLField("Webseite", blank=True)
    ask_for_car = models.BooleanField("Auto-Besitz abfragen", default=False)
    state = models.PositiveSmallIntegerField("Status", choices=STATE_CHOICES, default=PLANNED)

    class Meta:
        verbose_name = "Exkursion"
        verbose_name_plural = "Exkursionen"
        ordering = ['-date']

    def __str__(self) -> str:
        return self.title

    def get_state_color(self):
        colors = {
            self.PLANNED: 'is-light is-info',
            self.OPENED: 'is-light is-success',
            self.CLOSED: 'is-light is-danger',
            self.ARCHIVED: 'is-light',
        }
        return colors[self.state]


class Participant(models.Model):
    ENROLLED = 0
    APPROVED = 1
    REJECTED = 2
    STATE_CHOICES = [
        (ENROLLED, "Eingeschrieben"),
        (APPROVED, "Zugelassen"),
        (REJECTED, "Abgelehnt"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    excursion = models.ForeignKey(Excursion, on_delete=models.CASCADE)
    comment = models.TextField("Bemerkung", blank=True)
    is_driver = models.BooleanField("Fahrer", null=True)
    seats = models.PositiveSmallIntegerField("Sitzplätze", null=True)
    state = models.PositiveSmallIntegerField("Status", choices=STATE_CHOICES, default=ENROLLED)
    created_at = models.DateTimeField("Erstellt am", auto_now_add=True)

    class Meta:
        verbose_name = "Teilnehmer"
        verbose_name_plural = "Teilnehmer"
        ordering = ['created_at']
        constraints = [
            models.UniqueConstraint('user', 'excursion', name='unique_participant'),
            models.CheckConstraint(
                check=(
                    (Q(is_driver__isnull=True) & Q(seats__isnull=True)) |
                    (Q(is_driver__isnull=False) & Q(seats__isnull=False))
                ),
                name='driver_has_seats_or_null',
            )
        ]
        permissions = [
            ('contact_participant', "Can contact participant"),
        ]

    def __str__(self):
        return self.user.get_full_name()

    def get_state_color(self):
        colors = {
            self.ENROLLED: 'is-light is-info',
            self.APPROVED: 'is-light is-success',
            self.REJECTED: 'is-light is-danger',
        }
        return colors[self.state]

    def set_state(self, state) -> bool:
        states = [choice for choice, label in self.STATE_CHOICES]
        if state not in states:
            choices = ', '.join(states)
            raise ValueError(f"You can only set a state to one of the available choices. ({choices})")

        self.state = state
        self.save()

        template = PostmarkTemplate()
        payload = {
            'user_name': self.user.first_name,
            'excursion_name': self.excursion.title,
        }

        if state == self.APPROVED:
            error = template.send_message(self.user.email, 'participant-approved', payload)
        elif state == self.REJECTED:
            error = template.send_message(self.user.email, 'participant-rejected', payload)
        elif state == self.ENROLLED:
            raise NotImplementedError(f"Can not reset state to '{self.ENROLLED}'. Please request an administrator to "
                                      "use the available django-admin command.")
        else:
            error = None

        if error:
            logger.error("Failed to send email about changed state for participant '%s'", self.__str__())
            return False

        return True
