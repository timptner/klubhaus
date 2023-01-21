from django.views.generic import CreateView

from .models import User


class RegistrationView(CreateView):
    model = User
    fields = ['username', 'email']
