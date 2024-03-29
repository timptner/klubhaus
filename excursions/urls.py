from django.urls import path

from . import views

app_name = 'excursions'
urlpatterns = [
    path('', views.ExcursionListView.as_view(), name='excursion_list'),
    path('add/', views.ExcursionCreateView.as_view(), name='excursion_create'),
    path('<int:pk>/', views.ExcursionDetailView.as_view(), name='excursion_detail'),
    path('<int:pk>/edit/', views.ExcursionUpdateView.as_view(), name='excursion_update'),
    path('<int:pk>/register/', views.ParticipantCreateView.as_view(), name='participant_create'),
    path('<int:pk>/participants/', views.ParticipantListView.as_view(), name='participant_list'),
    path('<int:pk>/statistics/', views.ParticipantStatisticsView.as_view(), name='participant_statistics'),
    path('<int:pk>/contact/', views.ParticipantContactFormView.as_view(), name='participant_contact'),
    path('<int:pk>/draw/', views.ParticipantDrawFormView.as_view(), name='participant_draw'),
    path('<int:pk>/report/', views.participant_list_report, name='participant_list_export'),
    path('participants/<int:pk>/change_state/',
         views.ParticipantStateUpdateView.as_view(),
         name='participant_state_update'),
]
