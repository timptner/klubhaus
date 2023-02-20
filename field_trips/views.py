from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail, EmailMultiAlternatives
from django.shortcuts import redirect
from django.template import loader
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from field_trips.models import FieldTrip, Participant
from field_trips.forms import FieldTripForm
from markdown import markdown

User = get_user_model()


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

    def get_context_data(self, **kwargs):
        feedback = _validate_participant(self.object, self.request.user)
        context = super().get_context_data(**kwargs)
        context.update(**feedback)
        return context


def _validate_participant(field_trip: FieldTrip, user: User) -> dict:
    is_disabled = False
    conflicts = []

    if field_trip.is_expired:
        is_disabled = True
        conflicts.append(_("This field trip is expired."))

    if user.phone == '':
        is_disabled = True
        conflicts.append(_("Your mobile number is missing in your profile."))

    if user.pk in field_trip.participant_set.values_list('user', flat=True):
        is_disabled = True
        conflicts.append(_("You are already registered."))

    return {
        'is_disabled': is_disabled,
        'conflicts': conflicts,
    }


@login_required
def register(request, pk):
    field_trip = FieldTrip.objects.get(pk=pk)

    feedback = _validate_participant(field_trip, request.user)

    if feedback['is_disabled']:
        messages.error(request, _("You were not registered for this field trip."))
    else:
        Participant.objects.create(user=request.user, field_trip=field_trip)
        context = {
            'name': request.user.get_short_name(),
            'title': field_trip.title,
            'date': field_trip.date,
            'pk': field_trip.pk,
            'protocol': 'https' if request.is_secure() else 'http',
            'domain': get_current_site(request).domain,
        }
        send_mail(
            subject=_("Registration confirmation"),
            message=loader.render_to_string('field_trips/mail/confirm_registration.html', context, request),
            from_email=None,
            recipient_list=[request.user.email],
        )
        messages.success(request, _("You were successfully registered for this field trip."))

    return redirect(reverse('field_trips:field_trip_detail', kwargs={'pk': pk}))


class ParticipantListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Participant

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        return Participant.objects.filter(field_trip_id=self.kwargs['pk'])

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['field_trip'] = FieldTrip.objects.get(pk=self.kwargs['pk'])
        return context


class ParticipantDeleteView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = Participant
    success_message = _("Participant was removed successfully.")

    def get_success_url(self):
        return reverse('field_trips:participants', kwargs={'pk': self.object.field_trip.pk})

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        participant = Participant.objects.get(pk=self.kwargs['pk'])
        context = {
            'name': participant.user.get_short_name(),
            'title': participant.field_trip.title,
        }
        msg = loader.render_to_string('field_trips/mail/removed.md', context, self.request)
        email = EmailMultiAlternatives(
            subject=_("Removed from field trip"),
            body=msg,
            from_email=None,
            to=[participant.user.email],
            reply_to=['farafmb@ovgu.de'],
        )
        email.attach_alternative(markdown(msg), 'text/html')
        email.send()
        return super().form_valid(form)
