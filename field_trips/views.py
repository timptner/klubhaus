from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import redirect, render
from django.template import loader
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from field_trips.models import FieldTrip, Participant
from field_trips.forms import FieldTripForm
from markdown import markdown


class FieldTripListView(LoginRequiredMixin, ListView):
    model = FieldTrip


class FieldTripCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = FieldTrip
    form_class = FieldTripForm
    success_url = reverse_lazy('field_trips:field_trip_list')
    success_message = _("%(title)s was created successfully")
    permission_required = 'field_trips.add_field_trip'


class FieldTripDetailView(LoginRequiredMixin, DetailView):
    model = FieldTrip


class FieldTripUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = FieldTrip
    form_class = FieldTripForm
    success_message = _("%(title)s was updated successfully")
    permission_required = 'field_trips.change_field_trip'

    def get_success_url(self):
        return reverse('field_trips:field_trip_detail', kwargs={'pk': self.object.pk})


@login_required
def register(request, pk):
    field_trip = FieldTrip.objects.get(pk=pk)

    conflicts = []

    if field_trip.is_expired:
        conflicts.append(_("This field trip is expired."))

    if field_trip.participant_set.count() >= field_trip.seats:
        conflicts.append(_("All seats are taken."))

    if request.user.phone == '':
        conflicts.append(_("Your mobile number is missing in your profile."))

    if request.user.pk in field_trip.participant_set.values_list('user', flat=True):
        conflicts.append(_("You are already registered."))

    if request.method == 'POST':
        if conflicts:
            messages.error(request, _("You were not registered for this field trip."))
            return redirect(reverse('field_trips:register', kwargs={'pk': pk}))

        Participant.objects.create(user=request.user, field_trip=field_trip)

        mail_context = {
            'name': request.user.get_short_name(),
            'title': field_trip.title,
            'date': field_trip.date,
            'pk': field_trip.pk,
            'protocol': 'https' if request.is_secure() else 'http',
            'domain': get_current_site(request).domain,
        }
        msg = loader.render_to_string('field_trips/mail/confirm_registration.md', mail_context, request)
        email = EmailMultiAlternatives(
            subject=_("Registration confirmation"),
            body=msg,
            from_email=None,
            to=[request.user.email],
        )
        email.attach_alternative(markdown(msg), 'text/html')
        email.send()

        messages.success(request, _("You were successfully registered for this field trip."))

        return redirect(reverse('field_trips:field_trip_detail', kwargs={'pk': pk}))

    context = {
        'field_trip': field_trip,
        'conflicts': conflicts,
    }

    return render(request, 'field_trips/fieldtrip_register.html', context=context)


class FieldTripParticipantListView(PermissionRequiredMixin, ListView):
    model = Participant
    permission_required = 'field_trips.view_participant'

    def get_queryset(self):
        return Participant.objects.filter(field_trip_id=self.kwargs['pk'])

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['field_trip'] = FieldTrip.objects.get(pk=self.kwargs['pk'])
        return context


class ParticipantDeleteView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Participant
    permission_required = 'field_trips.delete_participant'

    def get_success_url(self):
        participant: Participant = self.object
        return reverse('field_trips:field_trip_participants', kwargs={'pk': participant.field_trip.pk})

    def get_success_message(self, cleaned_data):
        participant: Participant = self.object
        return _("%(first_name)s was removed successfully") % {'first_name': participant.user.first_name}

    def form_valid(self, form):
        response = super().form_valid(form)

        participant: Participant = self.object

        payload = {
            'name': participant.user.get_short_name(),
            'title': participant.field_trip.title,
        }

        text_content = loader.render_to_string(
            'field_trips/mail/removed.md',
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
