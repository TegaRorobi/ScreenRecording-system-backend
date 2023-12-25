
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

api_version = 'v1'

urlpatterns = [
    path(settings.ADMIN_URL + '/', admin.site.urls),
    path(f'api/{api_version}/', include('main.urls')),

    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    *static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
]
