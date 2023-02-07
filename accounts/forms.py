from accounts.models import User
from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth import forms as auth_forms
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from farafmb.forms import ModelForm

user_fields = list(auth_forms.UserCreationForm.Meta.fields)
user_fields.remove('username')


class UserCreateForm(auth_forms.UserCreationForm):
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text='<br>'.join(password_validation.password_validators_help_texts()),
    )

    class Meta(auth_forms.UserCreationForm.Meta):
        model = User
        fields = tuple(user_fields) + ('first_name', 'last_name', 'email')

    @staticmethod
    def send_mail(subject, email_template_name, context, from_email, to_email):
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        # email_message.attach_alternative(None, 'text/html')
        email_message.send()

    def save(self, commit=True, token_generator=None, request=None, use_https=False, email_template_name=None):
        user = super().save(commit=False)
        user.is_active = False
        if commit:
            user.save()

        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain

        context = {
            'site_name': site_name,
            'protocol': 'https' if use_https else 'http',
            'domain': domain,
            'user': user,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': token_generator.make_token(user),
        }
        subject = _("Activate your account")
        self.send_mail(subject, email_template_name, context, None, user.email)

        return user


class PasswordChangeForm(auth_forms.PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''

    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        help_text='<br>'.join(password_validation.password_validators_help_texts()),
    )


class SetPasswordForm(auth_forms.SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''

    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        help_text='<br>'.join(password_validation.password_validators_help_texts()),
    )