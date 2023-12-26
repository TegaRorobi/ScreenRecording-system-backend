
from django.contrib import admin
from django.urls import path, re_path, include
from django.conf.urls.static import static
from django.conf import settings
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

api_version = 'v1'

schema_view = get_schema_view(
    openapi.Info(
        title='Screen Recording API',
        description='An API backend for a screen recording browswer extension built with Django REST Framework',
        default_version=api_version,
        contact=openapi.Contact(email='support@screenrec.project'),
        terms_of_service=openapi.License('BSD License'),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path(settings.ADMIN_URL + '/', admin.site.urls),
    path(f'api/{api_version}/', include('main.urls')),

    re_path(f'api/{api_version}/swagger(?P<format>\.json|\.yaml)', schema_view.without_ui(), name='schema-json'),
    re_path(f'api/{api_version}/swagger/?$', schema_view.with_ui('swagger'), name='schema-swagger'),
    re_path(f'api/{api_version}/redoc/?$', schema_view.with_ui('redoc'), name='schema-redoc'),

    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    *static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
]
