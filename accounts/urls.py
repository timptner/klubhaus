from django.urls import path, include
from django.contrib.auth import views as auth_views

from . import views

app_name = 'accounts'

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('activate/<uidb64>/<token>/', views.ActivationView.as_view(), name='activate'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('register/', views.RegistrationView.as_view(), name='register'),
    path('register/success/', views.RegistrationSuccessView.as_view(), name='register_success')
]
