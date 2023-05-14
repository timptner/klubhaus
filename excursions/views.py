from markdown import markdown

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import redirect, render
from django.template import loader
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .models import Excursion, Participant
from .forms import ExcursionForm, ParticipantForm


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
        return reverse_lazy('excursions:excursion_detail', kwargs={'pk': self.kwargs['pk']})


class ParticipantListView(PermissionRequiredMixin, ListView):
    permission_required = 'excursions.view_participant'
    model = Participant

    def get_queryset(self):
        return Participant.objects.filter(excursion_id=self.kwargs['pk'])

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['excursion'] = Excursion.objects.get(pk=self.kwargs['pk'])
        return context


class ParticipantDeleteView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Participant
    permission_required = 'excursions.delete_participant'

    def get_success_url(self):
        participant: Participant = self.object
        return reverse_lazy('excursions:participant_list', kwargs={'pk': participant.excursion.pk})

    def get_success_message(self, cleaned_data):
        participant: Participant = self.object
        return _("%(first_name)s was removed successfully") % {'first_name': participant.user.first_name}

    def form_valid(self, form):
        response = super().form_valid(form)

        participant: Participant = self.object

        payload = {
            'name': participant.user.get_short_name(),
            'title': participant.excursion.title,
        }

        text_content = loader.render_to_string(
            'excursions/mail/removed.md',
            context=payload,
            request=self.request,
        )
        html_content = markdown(text_content)

        mail = EmailMultiAlternatives(
            subject=_("Removed from field trip"),
            body=text_content,
            to=[participant.user.email],
            reply_to=['farafmb@ovgu.de'],
        )
        mail.attach_alternative(html_content, 'text/html')
        mail.send()

        return response
