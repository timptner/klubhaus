from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path('', include('home.urls')),
    path('accounts/', include('accounts.urls')),
    path('field_trips/', include('field_trips.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
