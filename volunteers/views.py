from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from volunteers.forms import EventForm, VolunteerForm
from volunteers.models import Event, Volunteer


class EventListView(LoginRequiredMixin, ListView):
    model = Event
    ordering = ['-date']

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        personal_events = Volunteer.objects.filter(user=self.request.user).values_list('event__pk', flat=True)
        context['personal_events'] = personal_events
        return context


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
        context['is_disabled'] = event.state != Event.OPENED
        context['is_registered'] = event.volunteer_set.filter(user=self.request.user).exists()
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
        context['event'] = Event.objects.get(pk=self.kwargs['pk'])
        return context
