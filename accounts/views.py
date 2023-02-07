from accounts.models import User
from accounts.forms import UserCreateForm, PasswordChangeForm, SetPasswordForm
from datetime import timedelta
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView, UpdateView, TemplateView


class RegistrationView(UserPassesTestMixin, FormView):
    email_template_name = 'accounts/mail/activate_account.html'
    form_class = UserCreateForm
    success_url = reverse_lazy('accounts:register_success')
    template_name = 'accounts/user_form.html'
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
        current_time = timezone.now()
        context.update({
            'current_time': current_time,
            'link_expired': current_time + timedelta(seconds=settings.PASSWORD_RESET_TIMEOUT),
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


class ProfileView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    fields = ['first_name', 'last_name']
    template_name = 'accounts/user_profile.html'
    success_url = reverse_lazy('accounts:profile')
    success_message = _("Your profile was updated successfully.")

    def get_initial(self):
        return {
            'first_name': self.request.user.first_name,
            'last_name': self.request.user.last_name,
        }

    def get_object(self, queryset=None):
        return self.request.user


class PasswordChangeView(SuccessMessageMixin, auth_views.PasswordChangeView):
    form_class = PasswordChangeForm
    success_url = '.'
    success_message = _("Your password was updated successfully.")


class PasswordResetView(auth_views.PasswordResetView):
    email_template_name = 'registration/mail/password_reset.html'
    success_url = reverse_lazy('accounts:password_reset_done')


class PasswordResetConfirmView(SuccessMessageMixin, auth_views.PasswordResetConfirmView):
    form_class = SetPasswordForm
    success_url = reverse_lazy('accounts:login')
    success_message = _("Your password was updated successfully.")
