import csv

from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.template.defaultfilters import slugify
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView, FormView

from .forms import EventForm, VolunteerForm, VolunteerContactForm
from .models import Event, Volunteer


class EventListView(LoginRequiredMixin, ListView):
    model = Event
    queryset = Event.objects.exclude(state=Event.ARCHIVED)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)

        personal_events = Volunteer.objects.exclude(
            event__state=Event.ARCHIVED
        ).filter(
            user=self.request.user
        ).values_list('event__pk', flat=True)

        if personal_events:
            context['personal_events'] = personal_events

        return context


class EventArchiveListView(PermissionRequiredMixin, ListView):
    permission_required = 'volunteers.view_event'
    model = Event
    queryset = Event.objects.filter(state=Event.ARCHIVED)


class EventCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = 'volunteers.add_event'
    model = Event
    form_class = EventForm
    success_url = reverse_lazy('volunteers:event_list')
    success_message = "\"%(title)s\" wurde erfolgreich erstellt"


class EventDetailView(LoginRequiredMixin, DetailView):
    model = Event

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event: Event = self.object

        if event.state == Event.PREPARED:
            color = 'is-info'
            msg = "Die Registrierung ist im Moment noch geschlossen. Schaue in ein paar Tagen noch einmal vorbei."
        elif event.state == Event.CLOSED:
            color = 'is-danger'
            msg = "Die Registrierung ist beendet und wird nicht wieder geöffnet."
        elif event.state == Event.ARCHIVED:
            color = 'is-info'
            msg = "Die Veranstaltung wurde archiviert."
        elif event.volunteer_set.filter(user=self.request.user).exists():
            color = 'is-warning'
            msg = "Du bist für diese Veranstaltung bereits als Helfer registriert."
        elif not self.request.user.phone:
            url = reverse_lazy('accounts:profile')
            color = 'is-danger'
            msg = ("Bitte ergänze deine Mobilnummer in deinem "
                   f"<a href=\"{url}\">Profil</a>, um dich anmelden zu können.")
        else:
            color = None
            msg = None

        if color and msg:
            context['feedback'] = {
                'color': color,
                'message': msg,
            }

        return context


class EventUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = 'volunteers.change_event'
    model = Event
    form_class = EventForm
    success_message = "\"%(title)s\" wurde erfolgreich aktualisiert"

    def get_success_url(self):
        return reverse_lazy('volunteers:event_detail', kwargs={'pk': self.kwargs['pk']})


class VolunteerCreateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    model = Volunteer
    form_class = VolunteerForm
    success_message = "Du hast dich erfolgreich als freiwilliger Helfer angemeldet"

    def test_func(self):
        event = Event.objects.get(pk=self.kwargs['pk'])
        if event.state == Event.OPENED:
            return True

        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = Event.objects.get(pk=self.kwargs['pk'])
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['event'] = Event.objects.get(pk=self.kwargs['pk'])
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy('volunteers:event_detail', kwargs={'pk': self.kwargs['pk']})


class VolunteerListView(PermissionRequiredMixin, ListView):
    permission_required = 'volunteers.view_volunteer'
    model = Volunteer

    def get_queryset(self):
        return Volunteer.objects.filter(event__pk=self.kwargs['pk'])

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        event = Event.objects.get(pk=self.kwargs['pk'])
        context['event'] = event
        context['statistics'] = {
            'amount': event.volunteer_set.count(),
        }
        return context


class VolunteerContactView(PermissionRequiredMixin, FormView):
    permission_required = 'volunteers.contact_volunteer'
    form_class = VolunteerContactForm
    template_name = 'volunteers/volunteer_contact.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = Event.objects.get(pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        event = Event.objects.get(pk=self.kwargs['pk'])

        errors = form.send_mail(event)

        if errors:
            msg = f"Es kam zu einem Problem beim Versenden der E-Mails. Bitte einen Administrator kontaktieren."
            messages.error(self.request, msg)
        else:
            messages.success(self.request, f"Es wurden alle freiwilligen Helfer erfolgreich per E-Mails kontaktiert.")

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('volunteers:volunteer_list', kwargs={'pk': self.kwargs['pk']})


@permission_required('volunteers.view_volunteer')
def volunteer_export(request, pk):
    event = Event.objects.get(pk=pk)

    file_name = f'Freiwillige_{slugify(event.title)}.csv'
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': f'attachment; filename="{file_name}"'},
    )

    writer = csv.writer(response)
    writer.writerow(['Name', 'Mobilnummer', 'Fakultät', 'Bemerkung', 'Registrierung'])
    for volunteer in event.volunteer_set.order_by('user__first_name', 'user__last_name'):
        writer.writerow([
            volunteer.user.get_full_name(),
            f'tel:{volunteer.user.phone}',
            volunteer.user.get_faculty_display(),
            volunteer.comment,
            volunteer.created_at.isoformat(),
        ])

    return response
