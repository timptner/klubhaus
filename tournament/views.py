from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import login_required
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import formset_factory
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from tournament.forms import TournamentForm, TeamForm, PlayerForm
from tournament.models import Tournament, Team, Player


class TournamentListView(LoginRequiredMixin, ListView):
    model = Tournament


class TournamentCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = 'tournament.add_tournament'
    model = Tournament
    form_class = TournamentForm
    success_message = "%(title)s wurde erfolgreich erstellt"

    def get_success_url(self):
        return reverse_lazy('tournament:tournament_detail', kwargs={'pk': self.object.pk})


class TournamentDetailView(LoginRequiredMixin, DetailView):
    model = Tournament

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_registered'] = self.object.team_set.filter(captain=self.request.user).exists()
        context['team'] = Team.objects.filter(tournament=self.object, captain=self.request.user).first()
        return context


class TournamentUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = 'tournament.change_tournament'
    model = Tournament
    form_class = TournamentForm
    success_message = "%(title)s wurde erfolgreich geändert"

    def get_success_url(self):
        return reverse_lazy('tournament:tournament_detail', kwargs={'pk': self.object.pk})


@login_required
def registration(request, pk):
    tournament = Tournament.objects.get(pk=pk)

    if tournament.get_status() != 'open':
        raise PermissionDenied()

    # noinspection PyPep8Naming
    PlayerFormSet = formset_factory(PlayerForm, extra=1)

    if request.method == 'POST':
        team_form = TeamForm(request.POST, tournament=tournament, captain=request.user)
        player_formset = PlayerFormSet(request.POST)

        if team_form.is_valid() and player_formset.is_valid():
            team = team_form.save()

            for form in player_formset:
                player = form.save(commit=False)
                player.team = team
                player.save()

            messages.success(request, "Du hast dein Team erfolgreich für das Turnier angemeldet.")
            return redirect(reverse_lazy('tournament:my_team_list'))
    else:
        team_form = TeamForm(tournament=tournament, captain=request.user)
        player_formset = PlayerFormSet()

    context = {
        'tournament': tournament,
        'team_form': team_form,
        'player_formset': player_formset,
        'is_registered': tournament.team_set.filter(captain=request.user).exists(),
    }
    return render(request, 'tournament/registration.html', context=context)


class TeamListView(PermissionRequiredMixin, ListView):
    permission_required = 'tournament.view_team'

    def get_queryset(self):
        return Team.objects.filter(tournament=self.kwargs['pk']).all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['tournament'] = Tournament.objects.get(pk=self.kwargs['pk'])
        return context


class PersonalTeamListView(LoginRequiredMixin, ListView):
    template_name = 'tournament/my_team_list.html'

    def get_queryset(self):
        return Team.objects.filter(captain=self.request.user)
