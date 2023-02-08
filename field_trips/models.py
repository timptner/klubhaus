import markdown

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

User = get_user_model()


class FieldTrip(models.Model):  # TODO Add image and website link
    title = models.CharField(max_length=200)
    desc = models.TextField(_('description'))
    date = models.DateField(_('date of field trip'))
    seats = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ('-date',)

    def __str__(self) -> str:
        return self.title

    @property
    def is_expired(self) -> bool:
        return timezone.now().date() > self.date

    @property
    def enrollments(self) -> int:
        return self.participant_set.count()

    @property
    def available_seats(self) -> int:
        return self.seats - self.enrollments

    def desc_html(self) -> str:
        return markdown.markdown(self.desc)

    def progress(self) -> int:
        percent = self.enrollments / self.seats * 100
        return round(percent)


class Participant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    field_trip = models.ForeignKey(FieldTrip, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint('user', 'field_trip', name='unique_participant'),
        ]
        ordering = ('registered_at',)
