from markdown import markdown

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import redirect, render
from django.template import loader
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .models import Excursion, Participant
from .forms import ExcursionForm


class ExcursionListView(LoginRequiredMixin, ListView):
    model = Excursion


class ExcursionCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = Excursion
    form_class = ExcursionForm
    success_url = reverse_lazy('excursions:excursion_list')
    success_message = _("%(title)s was created successfully")
    permission_required = 'excursions.add_excursion'


class ExcursionDetailView(LoginRequiredMixin, DetailView):
    model = Excursion


class ExcursionUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Excursion
    form_class = ExcursionForm
    success_message = _("%(title)s was updated successfully")
    permission_required = 'excursions.change_excursion'

    def get_success_url(self):
        return reverse_lazy('excursions:excursion_detail', kwargs={'pk': self.object.pk})


@login_required
def register(request, pk):
    excursion = Excursion.objects.get(pk=pk)

    conflicts = []

    if excursion.is_expired:
        conflicts.append(_("This excursion is expired."))

    if excursion.participant_set.count() >= excursion.seats:
        conflicts.append(_("All seats are taken."))

    if request.user.phone == '':
        conflicts.append(_("Your mobile number is missing in your profile."))

    if request.user.pk in excursion.participant_set.values_list('user', flat=True):
        conflicts.append(_("You are already registered."))

    if request.method == 'POST':
        if conflicts:
            messages.error(request, _("You were not registered for this excursion."))
            return redirect(reverse_lazy('excursions:register', kwargs={'pk': pk}))

        Participant.objects.create(user=request.user, excursion=excursion)

        mail_context = {
            'name': request.user.get_short_name(),
            'title': excursion.title,
            'date': excursion.date,
            'pk': excursion.pk,
            'protocol': 'https' if request.is_secure() else 'http',
            'domain': get_current_site(request).domain,
        }
        msg = loader.render_to_string('excursions/mail/confirm_registration.md', mail_context, request)
        email = EmailMultiAlternatives(
            subject=_("Registration confirmation"),
            body=msg,
            from_email=None,
            to=[request.user.email],
        )
        email.attach_alternative(markdown(msg), 'text/html')
        email.send()

        messages.success(request, _("You were successfully registered for this excursion."))

        return redirect(reverse_lazy('excursions:excursion_detail', kwargs={'pk': pk}))

    context = {
        'excursion': excursion,
        'conflicts': conflicts,
    }

    return render(request, 'excursions/excursion_register.html', context=context)


class ParticipantListView(PermissionRequiredMixin, ListView):
    model = Participant
    permission_required = 'excursions.view_participant'

    def get_queryset(self):
        return Participant.objects.filter(field_trip_id=self.kwargs['pk'])

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
