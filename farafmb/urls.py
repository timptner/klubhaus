from django.urls import path, include

urlpatterns = [
    path('', include('home.urls')),
    path('accounts/', include('accounts.urls')),
]
