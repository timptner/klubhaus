from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import default_token_generator
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ImproperlyConfigured, ValidationError, PermissionDenied, BadRequest
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView, UpdateView, TemplateView, ListView, DetailView, CreateView

from klubhaus.mails import PostmarkTemplate
from tournament.models import Team

from .models import User, Modification
from .forms import (RegistrationForm, CustomAuthenticationForm, CustomPasswordChangeForm,
                    CustomSetPasswordForm, CustomPasswordResetForm, UserForm, ProfileForm, GroupForm,
                    MembershipForm)


class RegistrationFormView(UserPassesTestMixin, FormView):
    email_template_name = 'accounts/mail/activate_account.md'
    form_class = RegistrationForm
    success_url = reverse_lazy('accounts:register_success')
    template_name = 'accounts/registration.html'
    token_generator = default_token_generator

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def test_func(self):
        return self.request.user.is_anonymous

    def form_valid(self, form):
        link_expired = timezone.localtime(timezone.now() + timedelta(seconds=settings.PASSWORD_RESET_TIMEOUT))
        options = {
            'use_https': self.request.is_secure(),
            'token_generator': self.token_generator,
            'request': self.request,
            'link_expired': link_expired.strftime('%d.%m.%Y %H:%M %Z'),
        }
        form.save(**options)
        return super().form_valid(form)


class RegistrationSuccessView(UserPassesTestMixin, TemplateView):
    template_name = 'accounts/registration_success.html'

    def test_func(self):
        return self.request.user.is_anonymous

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['link_expired'] = timezone.now() + timedelta(seconds=settings.PASSWORD_RESET_TIMEOUT)
        return context


INTERNAL_ACTIVATION_SESSION_TOKEN = '_account_activation_token'


class ActivationView(TemplateView):
    activation_url_token = 'success'
    template_name = 'accounts/activation_success.html'
    token_generator = default_token_generator
    valid_link = False

    def dispatch(self, *args, **kwargs):
        if 'uidb64' not in kwargs or 'token' not in kwargs:
            raise ImproperlyConfigured(
                "The URL path must contain 'uidb64' and 'token' parameters."
            )

        self.valid_link = False
        user = self.get_user(kwargs['uidb64'])

        if user is not None:
            token = kwargs['token']
            if token == self.activation_url_token:
                session_token = self.request.session.get(INTERNAL_ACTIVATION_SESSION_TOKEN)
                if self.token_generator.check_token(user, session_token):
                    user.is_active = True
                    user.save()
                    self.valid_link = True
                    return super().dispatch(*args, **kwargs)
            else:
                if self.token_generator.check_token(user, token):
                    self.request.session[INTERNAL_ACTIVATION_SESSION_TOKEN] = token
                    redirect_url = self.request.path.replace(
                        token, self.activation_url_token
                    )
                    return HttpResponseRedirect(redirect_url)

        return self.render_to_response(self.get_context_data())

    @staticmethod
    def get_user(uidb64):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (
                TypeError,
                ValueError,
                OverflowError,
                User.DoesNotExist,
                ValidationError,
        ):
            user = None
        return user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.valid_link:
            context.update({
                'valid_link': True,
                'state': 'is-success',
            })
        else:
            context.update({
                'valid_link': False,
                'state': 'is-danger',
            })
        return context


class LoginView(auth_views.LoginView):
    form_class = CustomAuthenticationForm


class PasswordChangeView(SuccessMessageMixin, auth_views.PasswordChangeView):
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy('accounts:profile')
    success_message = _("Your password was updated successfully.")


class PasswordResetView(auth_views.PasswordResetView):
    form_class = CustomPasswordResetForm
    email_template_name = 'registration/mail/password_reset.md'
    success_url = reverse_lazy('accounts:password_reset_done')


class PasswordResetConfirmView(SuccessMessageMixin, auth_views.PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy('accounts:login')
    success_message = _("Your password was updated successfully.")


class UserListView(PermissionRequiredMixin, ListView):
    permission_required = 'accounts.view_user'
    model = User
    ordering = ['first_name', 'last_name']
    context_object_name = 'account_list'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['statistics'] = {
            'total': User.objects.count(),
            'active': User.objects.filter(is_active=True).count(),
            'inactive': User.objects.filter(is_active=False).count(),
            'staff': User.objects.filter(is_staff=True).count(),
        }
        return context


class UserDetailView(PermissionRequiredMixin, DetailView):
    permission_required = 'accounts.view_user'
    model = User
    context_object_name = 'account'


class UserUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = 'accounts.change_user'
    model = User
    form_class = UserForm
    success_message = _("%(first_name)s was updated successfully.")
    context_object_name = 'account'

    def get_success_url(self):
        return reverse_lazy('accounts:user_detail', kwargs={'pk': self.kwargs['pk']})


class ProfileView(LoginRequiredMixin, DetailView):
    template_name = 'accounts/profile.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_expired'] = Modification.objects.filter(
            user=self.request.user,
            state=Modification.REQUESTED,
        ).exists()
        return context


class ProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    template_name = 'accounts/profile_form.html'
    form_class = ProfileForm
    success_url = reverse_lazy('accounts:profile_modifications')
    success_message = "Änderung wurde erfolgreich beantragt"

    def test_func(self):
        has_pending_modifications = Modification.objects.filter(
            user=self.request.user,
            state=Modification.REQUESTED,
        ).exists()

        if has_pending_modifications:
            return False

        return True

    def get_object(self, queryset=None):
        return self.request.user


class ProfileTeamsView(LoginRequiredMixin, ListView):
    template_name = 'accounts/profile_teams.html'

    def get_queryset(self):
        return Team.objects.filter(captain=self.request.user).order_by('-tournament__date')


class ProfileModificationsView(LoginRequiredMixin, ListView):
    template_name = 'accounts/profile_modifications.html'

    def get_queryset(self):
        return Modification.objects.filter(user=self.request.user)


class GroupListView(PermissionRequiredMixin, ListView):
    permission_required = 'auth.view_group'
    model = Group


class GroupDetailView(PermissionRequiredMixin, DetailView):
    permission_required = 'auth.view_group'
    model = Group


class GroupCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = 'auth.add_group'
    model = Group
    form_class = GroupForm
    success_message = _("%(name)s was created successfully.")

    def get_success_url(self):
        return reverse_lazy('accounts:group_detail', kwargs={'pk': self.object.pk})


class GroupUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = 'auth.change_group'
    model = Group
    form_class = GroupForm
    success_message = _("%(name)s was updated successfully.")

    def get_success_url(self):
        return reverse_lazy('accounts:group_detail', kwargs={'pk': self.object.pk})


class GroupMembersView(PermissionRequiredMixin, SuccessMessageMixin, FormView):
    permission_required = ['auth.change_group', 'accounts.change_user']
    template_name = 'auth/group_members.html'
    form_class = MembershipForm
    success_message = _("Members were updated successfully.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        group = Group.objects.get(pk=self.kwargs['pk'])
        context.update({'group': group})

        return context

    def get_initial(self):
        initial = super().get_initial()

        group = Group.objects.get(pk=self.kwargs['pk'])
        initial.update({'users': group.user_set.all()})

        return initial

    def form_valid(self, form):
        group = Group.objects.get(pk=self.kwargs['pk'])
        old_users = group.user_set.all()
        new_users = form.cleaned_data['users']

        users_remove = [user for user in old_users if user not in new_users]
        for user in users_remove:
            user.groups.remove(group)

        users_add = [user for user in new_users if user not in old_users]
        for user in users_add:
            user.groups.add(group)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('accounts:group_detail', kwargs={'pk': self.kwargs['pk']})


class ModificationListView(PermissionRequiredMixin, ListView):
    permission_required = 'accounts.view_modification'
    model = Modification
    queryset = Modification.objects.filter(state=Modification.REQUESTED)


@permission_required(['accounts.change_modification', 'accounts.change_user'])
def handle_modification(request, pk):
    modification = Modification.objects.get(pk=pk)

    if modification.state != Modification.REQUESTED:
        raise PermissionDenied()

    if request.method == 'POST':
        if 'decision' in request.POST:
            decision = request.POST['decision']
            if decision == 'Akzeptieren':
                modification.state = Modification.ACCEPTED
                modification.save()

                user: User = modification.user

                for field, values in modification.content.items():
                    setattr(user, field, values['new'])

                user.save()

                template = PostmarkTemplate()
                payload = {
                    'name': user.first_name,
                }
                template.send_message(user.email, 'modification-accepted', payload)

            elif decision == 'Ablehnen':
                modification.state = Modification.REJECTED
                modification.save()

                user: User = modification.user

                template = PostmarkTemplate()
                payload = {
                    'name': user.first_name,
                }
                template.send_message(user.email, 'modification-rejected', payload)

            else:
                raise BadRequest()

            messages.success(request, "Antrag erfolgreich verarbeitet")
            return redirect(reverse_lazy('accounts:modification_list'))
        else:
            raise BadRequest()

    context = {
        'modification': modification,
    }

    return render(request, 'accounts/modification.html', context=context)
