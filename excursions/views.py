from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Sum
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView, FormView

from .models import Excursion, Participant
from .forms import (
    ExcursionForm, ParticipantForm, ExtendedParticipantForm, ParticipantStateForm, ParticipantContactForm,
    ParticipantDrawForm
)


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

        user = self.request.user
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
        elif excursion.participant_set.filter(user=user).exists():
            color = 'is-warning'
            message = "Du bist für diese Exkursion bereits angemeldet."
        elif not user.phone or not user.student:
            url = reverse_lazy('accounts:profile')
            color = 'is-danger'

            missing = []

            if not user.phone:
                missing.append('deine Mobilnummer')

            if not user.student:
                missing.append('deine Matrikelnummer')

            message = (f"Ergänze {' und '.join(missing)} <a href=\"{url}\">in deinem Profil</a>, "
                       "um dich anmelden zu können.")
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
    success_message = "Du hast dich erfolgreich zur Exkursion angemeldet"

    def test_func(self):
        user = self.request.user
        excursion = Excursion.objects.get(pk=self.kwargs['pk'])

        if excursion.state != Excursion.OPENED:
            return False
        elif not user.phone or not user.student:
            return False
        elif excursion.participant_set.filter(user=user).exists():
            return False
        else:
            return True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['excursion'] = Excursion.objects.get(pk=self.kwargs['pk'])
        return context

    def get_form_class(self):
        excursion = Excursion.objects.get(pk=self.kwargs['pk'])

        if excursion.ask_for_car:
            return ExtendedParticipantForm
        else:
            return ParticipantForm

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
        context['excursion'] = Excursion.objects.get(pk=self.kwargs['pk'])
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
        participant = Participant.objects.get(pk=self.kwargs['pk'])
        return reverse_lazy('excursions:participant_list', kwargs={'pk': participant.excursion.pk})


class ParticipantStatisticsView(PermissionRequiredMixin, TemplateView):
    permission_required = 'excursions.view_participant'
    template_name = 'excursions/participant_statistics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        excursion = Excursion.objects.get(pk=self.kwargs['pk'])

        context['excursion'] = excursion

        data = []
        for state, label in Participant.STATE_CHOICES:
            row = {
                'label': label,
                'people': excursion.participant_set.filter(state=state).count(),
                'cars': excursion.participant_set.filter(state=state, is_driver=True).count(),
                'seats': excursion.participant_set.filter(
                    state=state,
                    is_driver=True,
                ).aggregate(Sum('seats'))['seats__sum'],
            }
            data.append(row)

        context['data'] = data

        context['total'] = {
            'label': "Gesamt",
            'people': excursion.participant_set.count(),
            'cars': excursion.participant_set.filter(is_driver=True).count(),
            'seats': excursion.participant_set.filter(is_driver=True).aggregate(Sum('seats'))['seats__sum'],
        }

        return context


class ParticipantContactFormView(PermissionRequiredMixin, SuccessMessageMixin, FormView):
    permission_required = 'excursions.contact_participant'
    form_class = ParticipantContactForm
    template_name = 'excursions/participant_contact_form.html'
    success_message = "Empfänger erfolgreich kontaktiert"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['excursion'] = Excursion.objects.get(pk=self.kwargs['pk'])
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['excursion'] = Excursion.objects.get(pk=self.kwargs['pk'])
        return kwargs

    def form_valid(self, form):
        form.send_mail()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('excursions:participant_list', kwargs={'pk': self.kwargs['pk']})


class ParticipantDrawFormView(PermissionRequiredMixin, SuccessMessageMixin, FormView):
    permission_required = 'excursions.change_participant'
    form_class = ParticipantDrawForm
    template_name = 'excursions/participant_draw_form.html'
    success_message = "Erfolgreich %(amount)s Teilnehmer per Los zugelassen"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['excursion'] = Excursion.objects.get(pk=self.kwargs['pk'])
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['excursion'] = Excursion.objects.get(pk=self.kwargs['pk'])
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('excursions:participant_list', kwargs={'pk': self.kwargs['pk']})
