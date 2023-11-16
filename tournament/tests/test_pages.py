from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from tournament.models import Tournament


class TournamentListTest(TestCase):
    def setUp(self) -> None:
        self.path = reverse('tournament:tournament_list')
        self.user = User.objects.create_user(
            email='john.doe@example.org',
            password='secret',
        )
        self.user_staff = User.objects.create_user(
            email='jane.doe@example.org',
            password='secret',
            is_staff=True,
        )
        self.tournament1 = Tournament.objects.create(
            title="Turnier 1",
            date=date.today() + timedelta(days=5),
            players=4,
            registration_start=timezone.now(),
            registration_end=timezone.now() + timedelta(hours=8),
            is_visible=True,
        )
        self.tournament2 = Tournament.objects.create(
            title="Turnier 2",
            date=date.today() + timedelta(days=5),
            players=4,
            registration_start=timezone.now(),
            registration_end=timezone.now() + timedelta(hours=8),
            is_visible=False,
        )

    def test_visibility(self):
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.user)
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.tournament1.title)
        self.assertNotContains(response, self.tournament2.title)

        self.client.force_login(self.user_staff)
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.tournament1.title)
        self.assertContains(response, self.tournament2.title)
