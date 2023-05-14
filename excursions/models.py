from django.db import models

from accounts.models import User


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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    excursion = models.ForeignKey(Excursion, on_delete=models.CASCADE)
    comment = models.TextField("Bemerkung", blank=True)
    created_at = models.DateTimeField("Erstellt am", auto_now_add=True)

    class Meta:
        verbose_name = "Teilnehmer"
        verbose_name_plural = "Teilnehmer"
        ordering = ['created_at']
        constraints = [
            models.UniqueConstraint('user', 'excursion', name='unique_participant'),
        ]

    def __str__(self):
        return self.user.get_full_name()
