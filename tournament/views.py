from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import formset_factory
from django.core.exceptions import PermissionDenied
from django.core.mail import mail_admins
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from klubhaus.mails import PostmarkTemplate
from pprint import pprint
from tournament.forms import TournamentForm, TeamForm, PlayerForm, TeamDrawingForm
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


@permission_required('tournaments.change_team')
def team_drawing(request, pk):
    tournament = Tournament.objects.get(pk=pk)
    if request.method == 'POST':
        form = TeamDrawingForm(request.POST, tournament=tournament)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            message = form.cleaned_data['message']

            team_list = tournament.team_set.order_by('?').values_list('pk', flat=True)[:amount]
            updated = Team.objects.filter(pk__in=team_list).update(is_approved=True)

            if updated == 1:
                msg = f"Es wurde {updated} Team ausgelost."
            else:
                msg = f"Es wurden {updated} Teams ausgelost."

            messages.success(request, msg)

            recipients = []
            for team in Team.objects.filter(pk__in=team_list).all():
                recipient = (
                    team.captain.email,
                    {
                        'captain_name': team.captain.first_name,
                        'team_name': team.name,
                        'tournament_name': tournament.title,
                        'body': message,
                    },
                )
                recipients.append(recipient)

            template = PostmarkTemplate('team-drawing')
            count, errors = template.send_messages(recipients)

            if errors:
                msg = ("Es gab ein Problem beim Versenden von E-Mails an die Teams eines Turniers.\n\n"
                       f"Turnier: {tournament.title} (ID: {tournament.pk})\n\n"
                       f"{pprint(errors)}")
                mail_admins("Fehler beim E-Mail Versand", msg)

                msg = (f"Es gab ein Problem beim Versenden der E-Mails! Es wurden nur {count} Teams benachrichtigt. "
                       "Die Administratoren wurden bereits per E-Mail informiert.")
                messages.error(request, msg)
            else:
                msg = "Alle gelosten Teams wurden per E-Mail benachrichtigt."
                messages.success(request, msg)

            return redirect(reverse_lazy('tournament:team_list', kwargs={'pk': tournament.pk}))
    else:
        form = TeamDrawingForm(tournament=tournament)
    context = {
        'tournament': tournament,
        'has_approved_teams': tournament.team_set.filter(is_approved=True).exists(),
        'form': form,
    }
    return render(request, 'tournament/team_drawing.html', context=context)
