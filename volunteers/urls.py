from django.urls import path
from volunteers import views

app_name = 'volunteers'
urlpatterns = [
    path('', views.EventListView.as_view(), name='event_list'),
    path('add/', views.EventCreateView.as_view(), name='event_create'),
    path('<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('<int:pk>/edit/', views.EventUpdateView.as_view(), name='event_update'),
    path('<int:pk>/register/', views.VolunteerCreateView.as_view(), name='volunteer_create'),
]
