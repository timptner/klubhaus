from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from volunteers.forms import EventForm
from volunteers.models import Event


class EventListView(LoginRequiredMixin, ListView):
    model = Event


class EventCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = 'volunteers.add_event'
    model = Event
    form_class = EventForm
    success_url = reverse_lazy('volunteers:event_list')
    success_message = "\"%(title)s\" wurde erfolgreich erstellt"


class EventDetailView(LoginRequiredMixin, DetailView):
    model = Event


class EventUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = 'volunteers.change_event'
    model = Event
    form_class = EventForm
    success_message = "\"%(title)s\" wurde erfolgreich aktualisiert"

    def get_success_url(self):
        return reverse_lazy('volunteers:event_detail', kwargs={'pk': self.kwargs['pk']})
