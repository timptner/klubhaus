from django.urls import path
from volunteers import views

app_name = 'volunteers'
urlpatterns = [
    path('', views.EventListView.as_view(), name='event_list'),
    path('archived/', views.EventArchiveListView.as_view(), name='event_archive_list'),
    path('add/', views.EventCreateView.as_view(), name='event_create'),
    path('<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('<int:pk>/edit/', views.EventUpdateView.as_view(), name='event_update'),
    path('<int:pk>/register/', views.VolunteerCreateView.as_view(), name='volunteer_create'),
    path('<int:pk>/volunteers/', views.VolunteerListView.as_view(), name='volunteer_list'),
    path('<int:pk>/volunteers/contact/', views.VolunteerContactView.as_view(), name='volunteer_contact'),
    path('<int:pk>/volunteers/export/', views.volunteer_export, name='volunteer_export'),
]
