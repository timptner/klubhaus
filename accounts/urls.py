from accounts import views
from django.contrib.auth import views as auth_views
from django.urls import path

app_name = 'accounts'
urlpatterns = [
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/edit/', views.UserUpdateView.as_view(), name='user_edit'),
    path('user/<int:pk>/excursions/', views.UserExcursionsView.as_view(), name='user_excursions'),
    path('user/<int:pk>/teams/', views.UserTeamsView.as_view(), name='user_teams'),
    path('user/<int:pk>/events/', views.UserEventsView.as_view(), name='user_events'),
    path('user/<int:pk>/orders/', views.UserOrdersView.as_view(), name='user_orders'),
    path('groups/', views.GroupListView.as_view(), name='group_list'),
    path('groups/add/', views.GroupCreateView.as_view(), name='group_create'),
    path('groups/<int:pk>/', views.GroupDetailView.as_view(), name='group_detail'),
    path('groups/<int:pk>/edit/', views.GroupUpdateView.as_view(), name='group_update'),
    path('groups/<int:pk>/members/', views.GroupMembersView.as_view(), name='group_members'),
    path('activate/<uidb64>/<token>/', views.ActivationView.as_view(), name='activate'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password_change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('password_reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
    path('profile/teams/', views.ProfileTeamsView.as_view(), name='profile_teams'),
    path('profile/modifications/', views.ProfileModificationsView.as_view(), name='profile_modifications'),
    path('profile/excursions/', views.ProfileExcursionsView.as_view(), name='profile_excursions'),
    path('profile/orders/', views.ProfileOrdersView.as_view(), name='profile_orders'),
    path('register/', views.RegistrationFormView.as_view(), name='register'),
    path('register/success/', views.RegistrationSuccessView.as_view(), name='register_success'),
    path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('modifications/', views.ModificationListView.as_view(), name='modification_list'),
    path('modifications/<int:pk>/', views.handle_modification, name='modification_handle'),
]
