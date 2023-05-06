from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import formset_factory
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView, FormView
from tournament.forms import TournamentForm, TeamForm, PlayerForm, TeamDrawingForm, TeamContactForm
from tournament.models import Tournament, Team


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
        return Team.objects.filter(captain=self.request.user).order_by('-tournament__date')


@permission_required('tournaments.change_team')
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
    permission_required = 'tournaments.contact_team'
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
