from datetime import date, timedelta

from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from django.utils import timezone

from accounts.models import User
from tournament.models import Tournament
from tournament.views import TournamentListView, TournamentDetailView


class TournamentListViewTest(TestCase):
    def setUp(self) -> None:
        Tournament.objects.create(
            title="Turnier 1",
            date=date.today() + timedelta(days=2),
            players=4,
            registration_start=timezone.now(),
            registration_end=timezone.now() + timedelta(hours=8),
            is_visible=False,
        )
        Tournament.objects.create(
            title="Turnier 2",
            date=date.today() + timedelta(days=10),
            players=6,
            registration_start=timezone.now(),
            registration_end=timezone.now() + timedelta(hours=8),
            is_visible=True,
        )
        self.user = User.objects.create_user(
            email='max.mustermann@example.org',
            password='secret',
            is_staff=True,
        )

    def test_public_queryset(self):
        request = self.client.request()
        request.user = AnonymousUser()

        view = TournamentListView()
        view.setup(request)

        queryset = view.get_queryset()
        self.assertEqual(queryset.count(), 1)

    def test_private_queryset(self):
        request = self.client.request()
        request.user = self.user

        view = TournamentListView()
        view.setup(request)

        queryset = view.get_queryset()
        self.assertEqual(queryset.count(), 2)


class TournamentDetailViewTest(TestCase):
    def setUp(self) -> None:
        self.tournament1 = Tournament.objects.create(
            title="Turnier 1",
            date=date.today() + timedelta(days=2),
            players=4,
            registration_start=timezone.now(),
            registration_end=timezone.now() + timedelta(hours=8),
            is_visible=False,
        )
        self.tournament2 = Tournament.objects.create(
            title="Turnier 2",
            date=date.today() + timedelta(days=10),
            players=6,
            registration_start=timezone.now(),
            registration_end=timezone.now() + timedelta(hours=8),
            is_visible=True,
        )
        self.user = User.objects.create_user(
            email='max.mustermann@example.org',
            password='secret',
            is_staff=True,
        )

    def test_public_access_invisible_tournament(self):
        request = self.client.request()
        request.user = AnonymousUser()

        view = TournamentDetailView()
        view.setup(request, pk=self.tournament1.pk)

        has_access = view.test_func()
        self.assertFalse(has_access)

    def test_public_access_visible_tournament(self):
        request = self.client.request()
        request.user = AnonymousUser()

        view = TournamentDetailView()
        view.setup(request, pk=self.tournament2.pk)

        has_access = view.test_func()
        self.assertTrue(has_access)

    def test_private_access_invisible_tournament(self):
        request = self.client.request()
        request.user = self.user

        view = TournamentDetailView()
        view.setup(request, pk=self.tournament1)

        has_permission = view.test_func()
        self.assertTrue(has_permission)

    def test_private_access_visible_tournament(self):
        request = self.client.request()
        request.user = self.user

        view = TournamentDetailView()
        view.setup(request, pk=self.tournament2)

        has_permission = view.test_func()
        self.assertTrue(has_permission)
