from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import modelformset_factory
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView, FormView

from .forms import TournamentForm, TeamForm, PlayerForm, TeamDrawingForm, TeamContactForm, TeamStatusForm
from .models import Tournament, Team, Player


class TournamentListView(LoginRequiredMixin, ListView):
    model = Tournament

    def get_queryset(self):
        if self.request.user.is_staff:
            return Tournament.objects.all()
        else:
            return Tournament.objects.filter(is_visible=True)


class TournamentCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = 'tournament.add_tournament'
    model = Tournament
    form_class = TournamentForm
    success_message = "%(title)s wurde erfolgreich erstellt"

    def get_success_url(self):
        return reverse_lazy('tournament:tournament_detail', kwargs={'pk': self.object.pk})


class TournamentDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Tournament

    def test_func(self):
        if self.request.user.is_staff:
            return True

        tournament = self.get_object()
        if tournament.is_visible:
            return True

        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        team = Team.objects.filter(tournament=self.object, captain=self.request.user).first()
        context['team'] = team

        if self.object.get_state() == 'Abgelaufen':
            color = 'is-info'
            message = "Die Veranstaltung hat bereits stattgefunden."
        elif self.object.get_state() == 'Geschlossen':
            color = 'is-warning'
            message = "Die Anmeldung ist beendet."
        elif self.object.get_state() == 'Geplant':
            color = 'is-info'
            message = f"Die Anmeldung öffnet erst in einiger Zeit. Schaue später noch einmal vorbei!"
        elif self.object.team_set.filter(captain=self.request.user).exists():
            url = reverse_lazy('accounts:profile_teams')
            color = 'is-warning'
            message = (f"Du hast bereits das Team <strong><a href=\"{url}\">{team.name}</a></strong> für dieses "
                       "Turnier angemeldet.")
        else:
            color = None
            message = None

        if color and message:
            context['feedback'] = {
                'color': color,
                'message': message,
            }

        return context


class TournamentUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = 'tournament.change_tournament'
    model = Tournament
    form_class = TournamentForm
    success_message = "%(title)s wurde erfolgreich geändert"

    def get_success_url(self):
        return reverse_lazy('tournament:tournament_detail', kwargs={'pk': self.object.pk})


@login_required
def team_create(request, pk):
    tournament = Tournament.objects.get(pk=pk)

    if tournament.get_state() != 'Geöffnet':
        raise PermissionDenied()

    is_registered = tournament.team_set.filter(captain=request.user).exists()
    if is_registered:
        raise PermissionDenied()

    amount = tournament.players - 1
    # noinspection PyPep8Naming
    PlayerFormSet = modelformset_factory(model=Player, form=PlayerForm, min_num=amount, max_num=amount)

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
            return redirect(reverse_lazy('accounts:profile_teams'))
    else:
        team_form = TeamForm(tournament=tournament, captain=request.user)
        player_formset = PlayerFormSet(queryset=Player.objects.none())

    context = {
        'tournament': tournament,
        'team_form': team_form,
        'player_formset': player_formset,
    }

    return render(request, 'tournament/team_form.html', context=context)


class TeamListView(PermissionRequiredMixin, ListView):
    permission_required = 'tournament.view_team'

    def get_queryset(self):
        return Team.objects.filter(tournament=self.kwargs['pk']).all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        tournament = Tournament.objects.get(pk=self.kwargs['pk'])
        context['tournament'] = tournament
        amount_teams = Team.objects.filter(tournament=tournament).count()
        # Team captain does not count as player, therefore amount of teams must be added
        amount_players = Player.objects.filter(team__tournament=tournament).count() + amount_teams
        context['statistics'] = {
            'amount_teams': amount_teams,
            'amount_players': amount_players,
        }
        return context


@permission_required(['tournament.change_team', 'tournament.change_player'])
def team_update(request, pk):
    team = Team.objects.get(pk=pk)

    amount = team.tournament.players - team.player_set.count() - 1
    # noinspection PyPep8Naming
    PlayerFormSet = modelformset_factory(
        model=Player,
        form=PlayerForm,
        min_num=amount,
        max_num=amount,
    )

    if request.method == 'POST':
        team_form = TeamForm(request.POST, instance=team, tournament=team.tournament, captain=team.captain)
        player_formset = PlayerFormSet(request.POST, queryset=team.player_set.all())

        if team_form.is_valid() and player_formset.is_valid():
            team = team_form.save()
            for player_form in player_formset:
                player = player_form.save(commit=False)
                player.team = team
                player.save()

            messages.success(request, "Team erfolgreich aktualisiert")
            return redirect(reverse_lazy('tournament:team_list', kwargs={'pk': team.tournament.pk}))

    else:
        team_form = TeamForm(instance=team, tournament=team.tournament, captain=team.captain)
        player_formset = PlayerFormSet(queryset=team.player_set.all())

    context = {
        'team': team,
        'team_form': team_form,
        'player_formset': player_formset,
    }

    return render(request, 'tournament/team_form.html', context=context)


@permission_required('tournament.change_team')
def team_drawing(request, pk):
    tournament = Tournament.objects.get(pk=pk)
    if request.method == 'POST':
        form = TeamDrawingForm(request.POST, tournament=tournament)
        if form.is_valid():
            amount = form.cleaned_data['amount']

            approved = 0
            rejected = 0
            for index, team in enumerate(tournament.team_set.filter(state=Team.ENROLLED).order_by('?')):
                if index < amount:
                    is_updated = team.set_state(Team.APPROVED)
                    if is_updated:
                        approved += 1
                else:
                    is_updated = team.set_state(Team.REJECTED)
                    if is_updated:
                        rejected += 1

            if amount == approved:
                total = approved + rejected
                if total == 1:
                    msg = f"Es wurde {total} Team per Los entschieden. ({approved} Zugelassen, {rejected} Abgelehnt)"
                else:
                    msg = f"Es wurden {total} Teams per Los entschieden. ({approved} Zugelassen, {rejected} Abgelehnt)"

                messages.success(request, msg)
            else:
                msg = f"Es gab ein Problem beim Losen der Teams. Bitte einen Administrator kontaktieren."
                messages.error(request, msg)

            return redirect(reverse_lazy('tournament:team_list', kwargs={'pk': tournament.pk}))
    else:
        form = TeamDrawingForm(tournament=tournament)
    context = {
        'tournament': tournament,
        'form': form,
    }
    return render(request, 'tournament/team_drawing.html', context=context)


class TeamContactView(PermissionRequiredMixin, FormView):
    permission_required = 'tournament.contact_team'
    form_class = TeamContactForm
    template_name = 'tournament/team_contact.html'

    def get_success_url(self):
        return reverse_lazy('tournament:team_list', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tournament'] = Tournament.objects.get(pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        tournament = Tournament.objects.get(pk=self.kwargs['pk'])

        errors = form.send_email(tournament)

        if errors:
            email_list = ', '.join(errors.keys())

            msg = ("Es gab ein Problem beim Sender einiger E-Mails. Die folgenden Benutzer haben aufgrund eines "
                   f"Problems keine E-Mail erhalten: {email_list}.")

            messages.error(self.request, msg)
        else:
            total = tournament.team_set.filter(state=Team.APPROVED).count()

            if total == 1:
                msg = f"Es wurde {total} Team erfolgreich per E-Mail kontaktiert."
            else:
                msg = f"Es wurden {total} Teams erfolgreich per E-Mail kontaktiert."

            messages.success(self.request, msg)

        return super().form_valid(form)


class TeamStateChangeView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = 'tournament.change_team'
    model = Team
    form_class = TeamStatusForm
    template_name = 'tournament/team_status_form.html'
    success_message = "Der Status vom Team \"%(name)s\" wurde erfolgreich geändert."

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            name=self.object.name,
        )

    def get_success_url(self):
        return reverse_lazy('tournament:team_list', kwargs={'pk': self.object.tournament.pk})
