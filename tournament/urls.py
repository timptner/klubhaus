from django.urls import path
from tournament import views

app_name = 'tournament'
urlpatterns = [
    path('', views.TournamentListView.as_view(), name='tournament_list'),
    path('add/', views.TournamentCreateView.as_view(), name='tournament_create'),
    path('<int:pk>/', views.TournamentDetailView.as_view(), name='tournament_detail'),
    path('<int:pk>/edit/', views.TournamentUpdateView.as_view(), name='tournament_update'),
    path('<int:pk>/teams/', views.TeamListView.as_view(), name='team_list'),
    path('<int:pk>/teams/add/', views.registration, name='registration'),
    path('<int:pk>/teams/draw/', views.team_drawing, name='team_drawing'),
    path('<int:pk>/teams/contact/', views.TeamContactView.as_view(), name='team_contact'),
    path('teams/<int:pk>/change_status/', views.TeamStateChangeView.as_view(), name='change_team_status'),
    path('teams/', views.PersonalTeamListView.as_view(), name='my_team_list'),
]
