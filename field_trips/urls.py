from django.urls import path
from field_trips import views

app_name = 'field_trips'
urlpatterns = [
    path('', views.FieldTripListView.as_view(), name='field_trip_list'),
    path('add/', views.FieldTripCreateView.as_view(), name='field_trip_create'),
    path('<int:pk>/', views.FieldTripDetailView.as_view(), name='field_trip_detail'),
    path('<int:pk>/edit/', views.FieldTripUpdateView.as_view(), name='field_trip_update'),
    path('<int:pk>/register/', views.register, name='register'),
    path('<int:pk>/participants/', views.FieldTripParticipantListView.as_view(), name='field_trip_participants'),
    path('participants/<int:pk>/delete/', views.ParticipantDeleteView.as_view(), name='participant_delete'),
]
