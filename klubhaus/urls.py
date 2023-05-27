from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path('', include('home.urls')),
    path('accounts/', include('accounts.urls')),
    path('events/', include('volunteers.urls')),
    path('excursions/', include('excursions.urls')),
    path('merchandise/', include('merchandise.urls')),
    path('tournament/', include('tournament.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
