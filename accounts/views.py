from django.views.generic import CreateView, UpdateView
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.translation import gettext_lazy as _

from .models import User


class RegistrationView(CreateView):
    model = User
    fields = ['first_name', 'last_name', 'username', 'email', 'password']


class ProfileView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    fields = ['first_name', 'last_name']
    template_name = 'accounts/user_profile.html'
    success_url = '.'
    success_message = _("Your profile was updated successfully.")

    def get_initial(self):
        return {
            'first_name': self.request.user.first_name,
            'last_name': self.request.user.last_name,
        }

    def get_object(self, queryset=None):
        return self.request.user
