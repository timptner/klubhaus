from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from .models import Excursion, Participant
from .forms import ExcursionForm, ParticipantForm, ParticipantStateForm


class ExcursionListView(LoginRequiredMixin, ListView):
    model = Excursion


class ExcursionCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = 'excursions.add_excursion'
    model = Excursion
    form_class = ExcursionForm
    success_url = reverse_lazy('excursions:excursion_list')
    success_message = "%(title)s wurde erfolgreich erstellt"


class ExcursionDetailView(LoginRequiredMixin, DetailView):
    model = Excursion

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        excursion = Excursion.objects.get(pk=self.kwargs['pk'])
        if excursion.state == Excursion.PLANNED:
            color = 'is-info'
            message = "Die Anmeldung ist im Moment noch geschlossen. Schaue in ein paar Tagen noch einmal vorbei."
        elif excursion.state == Excursion.CLOSED:
            color = 'is-danger'
            message = "Die Anmeldung ist beendet und wird nicht wieder geöffnet."
        elif excursion.state == Excursion.ARCHIVED:
            color = 'is-info'
            message = "Die Veranstaltung wurde archiviert."
        elif excursion.participant_set.filter(user=self.request.user).exists():
            color = 'is-warning'
            message = "Du bist für diese Exkursion bereits angemeldet."
        elif not self.request.user.phone:
            url = reverse_lazy('accounts:profile')
            color = 'is-danger'
            message = ("Bitte ergänze deine Mobilnummer in deinem "
                       f"<a href=\"{url}\">Profil</a>, um dich anmelden zu können.")
        else:
            color = None
            message = None

        if color and message:
            context['feedback'] = {
                'color': color,
                'message': message,
            }
        return context


class ExcursionUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Excursion
    form_class = ExcursionForm
    success_message = "%(title)s wurde erfolgreich aktualisiert"
    permission_required = 'excursions.change_excursion'

    def get_success_url(self):
        return reverse_lazy('excursions:excursion_detail', kwargs={'pk': self.object.pk})


class ParticipantCreateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    model = Participant
    form_class = ParticipantForm
    success_message = "Du hast dich erfolgreich zur Exkursion angemeldet"

    def test_func(self):
        excursion = Excursion.objects.get(pk=self.kwargs['pk'])
        if excursion.state != Excursion.OPENED:
            return False

        if not self.request.user.phone:
            # TODO add matrikel check
            return False

        if excursion.participant_set.filter(user=self.request.user).exists():
            return False

        return True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['excursion'] = Excursion.objects.get(pk=self.kwargs['pk'])
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user': self.request.user,
            'excursion': Excursion.objects.get(pk=self.kwargs['pk'])
        })
        return kwargs

    def get_success_url(self):
        return reverse_lazy('accounts:profile_excursions')


class ParticipantListView(PermissionRequiredMixin, ListView):
    permission_required = 'excursions.view_participant'
    model = Participant

    def get_queryset(self):
        return Participant.objects.filter(excursion_id=self.kwargs['pk'])

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        excursion = Excursion.objects.get(pk=self.kwargs['pk'])

        context['excursion'] = excursion
        context['statistics'] = {
            'total': excursion.participant_set.count(),
            'enrolled': excursion.participant_set.filter(state=Participant.ENROLLED).count(),
            'approved': excursion.participant_set.filter(state=Participant.APPROVED).count(),
            'rejected': excursion.participant_set.filter(state=Participant.REJECTED).count(),
        }

        return context


class ParticipantStateUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = 'excursions.change_participant'
    model = Participant
    form_class = ParticipantStateForm
    template_name = 'excursions/participant_state_form.html'

    def get_success_message(self, cleaned_data):
        participant: Participant = self.object
        return f"Status von {participant.user.get_full_name()} erfolgreich geändert"

    def get_success_url(self):
        return reverse_lazy('excursions:participant_list', kwargs={'pk': self.kwargs['pk']})
