from django.urls import path
from field_trips import views

app_name = 'field_trips'
urlpatterns = [
    path('', views.FieldTripPublicListView.as_view(), name='field_trips_public'),
    path('list/', views.FieldTripListView.as_view(), name='field_trips'),
    path('<int:pk>/', views.FieldTripDetailView.as_view(), name='field_trip_detail'),
    path('<int:pk>/edit/', views.FieldTripUpdateView.as_view(), name='field_trip_edit'),
    path('<int:pk>/register/', views.register, name='register'),
    path('<int:pk>/participants/', views.ParticipantListView.as_view(), name='participants'),
    path('add/', views.FieldTripCreateView.as_view(), name='field_trip_add'),
    path('participants/<int:pk>/delete/', views.ParticipantDeleteView.as_view(), name='participant_delete'),
]
