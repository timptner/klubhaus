from django.urls import path

from . import views

app_name = 'home'

urlpatterns = [
    path('', views.LandingPage.as_view(), name='landing-page'),
    path('site_notice/', views.SiteNoticePage.as_view(), name='site-notice'),
]
