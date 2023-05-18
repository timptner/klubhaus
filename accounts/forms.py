from accounts.models import User, Modification
from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import (UserCreationForm, AuthenticationForm, PasswordResetForm,
                                       PasswordChangeForm, SetPasswordForm)
from django.contrib.auth.models import Group
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from markdown import markdown


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'student', 'faculty']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'input'}),
            'last_name': forms.TextInput(attrs={'class': 'input'}),
            'email': forms.EmailInput(attrs={'class': 'input'}),
            'phone': forms.TextInput(attrs={'class': 'input'}),
            'student': forms.TextInput(attrs={'class': 'input'}),
        }
        help_texts = {
            'email': "Bitte verwende deine studentische E-Mail-Adressen der Otto-von-Guericke-Universität.",
            'phone': "Wenn du an Exkursionen teilnehmen möchtest oder dich als Helfer für eine unserer Veranstaltungen "
                     "meldest, solltest du bereits jetzt deine Mobilnummer angeben, um dir später zusätzliche "
                     "Wartezeit bei der Anmeldung zu ersparen.",
            'student': "Wenn du an Exkursionen teilnehmen möchtest solltest du bereits jetzt deine Matrikelnummer "
                       "angeben, um dir später zusätzliche Wartezeit bei der Anmeldung zu ersparen.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ['first_name', 'last_name']:
            self.fields[field].required = True

        self.fields[self._meta.model.USERNAME_FIELD].widget.attrs.update({'autofocus': False})
        self.fields['first_name'].widget.attrs.update({'autofocus': True})

        for field in ['password1', 'password2']:
            self.fields[field].widget.attrs.update({'class': 'input'})

        self.fields['password1'].help_text = '<br>'.join(password_validation.password_validators_help_texts())

    def clean_phone(self):
        data = self.cleaned_data['phone']
        data = data.replace(' ', '')
        return data

    @staticmethod
    def send_mail(subject, email_template_name, context, from_email, to_email):
        body = loader.render_to_string(email_template_name, context)

        email = EmailMultiAlternatives(
            subject=subject,
            body=body,
            from_email=from_email,
            to=[to_email],
        )
        email.attach_alternative(markdown(body), 'text/html')
        email.send()

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


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ['username', 'password']:
            self.fields[field].widget.attrs.update({'class': 'input'})


class CustomPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'class': 'input'})

    def send_mail(self, subject_template_name, email_template_name, context,
                  from_email, to_email, html_email_template_name=None):
        if html_email_template_name:
            raise NotImplementedError()

        subject = _("Reset password")
        body = loader.render_to_string(email_template_name, context)

        email = EmailMultiAlternatives(
            subject=subject,
            body=body,
            from_email=from_email,
            to=[to_email],
        )
        email.attach_alternative(markdown(body), "text/html")
        email.send()


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ['old_password', 'new_password1', 'new_password2']:
            self.fields[field].widget.attrs.update({'class': 'input'})

        self.fields['new_password1'].help_text = '<br>'.join(password_validation.password_validators_help_texts())


class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ['new_password1', 'new_password2']:
            self.fields[field].widget.attrs.update({'class': 'input'})

        self.fields['new_password1'].help_text = '<br>'.join(password_validation.password_validators_help_texts())


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'student', 'faculty',
                  'is_active', 'is_staff', 'is_superuser']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'input'}),
            'last_name': forms.TextInput(attrs={'class': 'input'}),
            'email': forms.EmailInput(attrs={'class': 'input'}),
            'phone': forms.TextInput(attrs={'class': 'input'}),
            'student': forms.TextInput(attrs={'class': 'input'}),
        }
        help_texts = {
            'is_active': "Legt fest, ob der Benutzer sich anmelden kann. Neu registrierte Benutzer sind standardmäßig "
                         "deaktiviert, da sie erst ihre E-Mail-Adresse validieren müssen.",
            'is_staff': "Legt fest, ob der Benutzer bestimmte Seiten und Schaltflächen zur Verwaltung der Angebote "
                        "sehen kann. Dieser Status vergibt noch keine Berechtigungen!",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ['first_name', 'last_name']:
            self.fields[field].required = True


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'student', 'faculty']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'input'}),
            'last_name': forms.TextInput(attrs={'class': 'input'}),
            'email': forms.EmailInput(attrs={'class': 'input'}),
            'phone': forms.TextInput(attrs={'class': 'input'}),
            'student': forms.TextInput(attrs={'class': 'input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original = {}
        for field in self.Meta.fields:
            self.original[field] = getattr(self.instance, field)

        for field in ['first_name', 'last_name']:
            self.fields[field].required = True

    def clean_phone(self):
        data = self.cleaned_data['phone']
        data = data.replace(' ', '')
        return data

    def _get_diff(self) -> dict:
        diff = {}
        for field in self.Meta.fields:
            old_value = self.original[field]
            new_value = self.cleaned_data[field]
            if old_value == new_value:
                continue

            diff[field] = {
                'old': old_value,
                'new': new_value,
            }

        print(diff)

        return diff

    def clean(self):
        cleaned_data = super().clean()

        is_valid = all([field in cleaned_data.keys() for field in self.Meta.fields])
        if is_valid:
            diff = self._get_diff()
            if len(diff) == 0:
                raise ValidationError("Es wurden keine Änderungen vorgenommen.")

    def save(self, commit=True):
        diff = self._get_diff()

        Modification.objects.create(
            user=self.instance,
            content=diff,
        )

        return self.instance


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'permissions']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'input'})
        self.fields['permissions'].widget.attrs.update({'size': 10})
        self.fields['permissions'].help_text = _("You can select multiple permissions with <code>SHIFT</code>. To "
                                                 "select or unselect a single permission use <code>CMD</code> or "
                                                 "<code>STRG</code>.")


class MembershipForm(forms.Form):
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={'size': 10}),
        help_text=_("You can select multiple users with <code>SHIFT</code>. To select or unselect a single user use "
                    "<code>CMD</code> or <code>STRG</code>."),
    )
