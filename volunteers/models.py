from accounts.models import User
from django.db import models


class Event(models.Model):
    PREPARED = 0
    OPENED = 1
    CLOSED = 2
    ARCHIVED = 3
    STATE_CHOICES = [
        (PREPARED, "Vorbereitet"),
        (OPENED, "Geöffnet"),
        (CLOSED, "Geschlossen"),
        (ARCHIVED, "Archiviert"),
    ]
    title = models.CharField("Titel", max_length=50, unique=True)
    date = models.DateField("Datum")
    desc = models.TextField("Beschreibung")
    state = models.SmallIntegerField("Status", choices=STATE_CHOICES, default=PREPARED)

    class Meta:
        verbose_name = "Veranstaltung"
        verbose_name_plural = "Veranstaltungen"
        ordering = ['-date']

    def __str__(self):
        return self.title

    def get_state_color(self):
        colors = {
            self.PREPARED: 'is-light is-info',
            self.OPENED: 'is-light is-success',
            self.CLOSED: 'is-light is-danger',
            self.ARCHIVED: 'is-light',
        }
        return colors[self.state]


class Volunteer(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField("Bemerkung")
    created_at = models.DateTimeField("Erstellt am", auto_now_add=True)

    class Meta:
        verbose_name = "Freiwilliger"
        verbose_name_plural = "Freiwillige"
        ordering = ['created_at']
        constraints = [
            models.UniqueConstraint(fields=['event', 'user'], name='unique_event_volunteer'),
        ]
        permissions = [
            ('contact_volunteer', "Can contact volunteer"),
        ]

    def __str__(self):
        return self.user.get_full_name()
