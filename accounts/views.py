from accounts.models import User
from accounts.forms import (CustomUserCreateForm, CustomAuthenticationForm, CustomPasswordChangeForm,
                            CustomSetPasswordForm, CustomPasswordResetForm, UserForm, ProfileForm)
from datetime import timedelta
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView, UpdateView, TemplateView, ListView, DetailView


class RegistrationView(UserPassesTestMixin, FormView):
    email_template_name = 'accounts/mail/activate_account.md'
    form_class = CustomUserCreateForm
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
        options = {
            'use_https': self.request.is_secure(),
            'token_generator': self.token_generator,
            'email_template_name': self.email_template_name,
            'request': self.request,
        }
        form.save(**options)
        return super().form_valid(form)


class RegistrationSuccessView(UserPassesTestMixin, TemplateView):
    template_name = 'accounts/registration_success.html'

    def test_func(self):
        return self.request.user.is_anonymous

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'link_expired': timezone.now() + timedelta(seconds=settings.PASSWORD_RESET_TIMEOUT),
        })
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
    permission_required = 'auth.view_user'
    model = User
    ordering = ['first_name', 'last_name']
    context_object_name = 'account_list'


class UserDetailView(PermissionRequiredMixin, DetailView):
    permission_required = 'auth.view_user'
    model = User
    context_object_name = 'account'


class UserUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = 'auth.change_user'
    model = User
    form_class = UserForm
    success_message = _("%(first_name)s was updated successfully.")
    context_object_name = 'account'

    def get_success_url(self):
        return reverse('accounts:user_detail', kwargs={'pk': self.kwargs['pk']})


class ProfileView(LoginRequiredMixin, DetailView):
    template_name = 'accounts/profile.html'

    def get_object(self, queryset=None):
        return self.request.user


class ProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = 'accounts/profile_form.html'
    form_class = ProfileForm
    success_url = reverse_lazy('accounts:profile')
    success_message = _("Your profile was updated successfully.")

    def get_object(self, queryset=None):
        return self.request.user
