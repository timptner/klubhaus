from django.urls import path

from . import views

app_name = 'home'

urlpatterns = [
    path('', views.LandingPage.as_view(), name='landing_page'),
    path('site_notice/', views.SiteNoticePage.as_view(), name='site_notice'),
    path('privacy_policy/', views.PrivacyPolicyPage.as_view(), name='privacy_policy'),
]
