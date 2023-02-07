from accounts import views
from django.contrib.auth import views as auth_views
from django.urls import path, include

app_name = 'accounts'

urlpatterns = [
    path('', views.UserListView.as_view(), name='users'),
    path('<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('<int:pk>/edit/', views.UserUpdateView.as_view(), name='user_edit'),
    path('activate/<uidb64>/<token>/', views.ActivationView.as_view(), name='activate'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password_change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('password_reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('register/', views.RegistrationView.as_view(), name='register'),
    path('register/success/', views.RegistrationSuccessView.as_view(), name='register_success'),
    path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
