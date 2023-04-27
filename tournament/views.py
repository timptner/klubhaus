from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from tournament.forms import TournamentForm
from tournament.models import Tournament


class TournamentListView(LoginRequiredMixin, ListView):
    model = Tournament


class TournamentCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = 'tournament.add_tournament'
    model = Tournament
    form_class = TournamentForm
    success_message = "%(title)s wurde erfolgreich erstellt"

    def get_success_url(self):
        return reverse_lazy('tournament:tournament_detail', kwargs={'pk': self.object.pk})


class TournamentDetailView(PermissionRequiredMixin, DetailView):
    permission_required = 'tournament.view_tournament'
    model = Tournament


class TournamentUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = 'tournament.change_tournament'
    model = Tournament
    form_class = TournamentForm
    success_message = "%(title)s wurde erfolgreich geändert"

    def get_success_url(self):
        return reverse_lazy('tournament:tournament_detail', kwargs={'pk': self.object.pk})
