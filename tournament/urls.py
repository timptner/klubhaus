from django.urls import path
from tournament import views

app_name = 'tournament'
urlpatterns = [
    path('', views.TournamentListView.as_view(), name='tournament_list'),
    path('add/', views.TournamentCreateView.as_view(), name='tournament_create'),
    path('<int:pk>/', views.TournamentDetailView.as_view(), name='tournament_detail'),
    path('<int:pk>/edit/', views.TournamentUpdateView.as_view(), name='tournament_update'),
]
