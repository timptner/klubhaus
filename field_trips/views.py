from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from field_trips.models import FieldTrip, Participant
from field_trips.forms import FieldTripForm


class FieldTripListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = FieldTrip

    def test_func(self):
        return self.request.user.is_staff


class FieldTripCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = FieldTrip
    form_class = FieldTripForm
    success_url = reverse_lazy('field_trips:field_trips')

    def test_func(self):
        return self.request.user.is_staff


class FieldTripUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = FieldTrip
    form_class = FieldTripForm
    success_message = _("Field Trip was updated successfully.")

    def test_func(self):
        return self.request.user.is_staff

    def get_success_url(self):
        return reverse('field_trips:field_trip_detail', kwargs={'pk': self.object.pk})


class FieldTripPublicListView(LoginRequiredMixin, ListView):
    template_name = 'field_trips/fieldtrip_public_list.html'
    model = FieldTrip
    queryset = FieldTrip.objects.filter(date__gt=timezone.now())


class FieldTripDetailView(LoginRequiredMixin, DetailView):
    model = FieldTrip


@login_required
def register(request, pk):
    field_trip = FieldTrip.objects.get(pk=pk)

    is_registered = Participant.objects.filter(user=request.user, field_trip=field_trip).exists()
    if not is_registered:
        Participant.objects.create(user=request.user, field_trip=field_trip)
        messages.success(request, _("You were successfully registered for this field trip."))
    else:
        messages.error(request, _("You are already registered for this field trip."))

    return redirect(reverse('field_trips:field_trip_detail', kwargs={'pk': pk}))


class ParticipantListView(ListView):
    model = Participant

    def get_queryset(self):
        return Participant.objects.filter(field_trip_id=self.kwargs['pk'])

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['field_trip'] = FieldTrip.objects.get(pk=self.kwargs['pk'])
        return context
