
from django.contrib import admin
from django.urls import path, include
from django.conf import settings

api_version = 'v1'

urlpatterns = [
    path(settings.ADMIN_URL + '/', admin.site.urls),
    path(f'api/{api_version}/', include('main.urls')),
]
