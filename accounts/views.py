from django.views.generic import CreateView
from django.contrib.auth import views as auth_views

from .models import User


class RegistrationView(CreateView):
    model = User
    fields = ['first_name', 'last_name', 'username', 'email', 'password']
