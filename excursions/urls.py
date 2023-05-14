from django.urls import path

from . import views

app_name = 'excursions'
urlpatterns = [
    path('', views.ExcursionListView.as_view(), name='excursion_list'),
    path('add/', views.ExcursionCreateView.as_view(), name='excursion_create'),
    path('<int:pk>/', views.ExcursionDetailView.as_view(), name='excursion_detail'),
    path('<int:pk>/edit/', views.ExcursionUpdateView.as_view(), name='excursion_update'),
    path('<int:pk>/register/', views.register, name='register'),
    path('<int:pk>/participants/', views.ParticipantListView.as_view(), name='participant_list'),
    path('participants/<int:pk>/delete/', views.ParticipantDeleteView.as_view(), name='participant_delete'),
]
