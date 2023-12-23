
from django.urls import re_path
from .views import *

app_name = 'main'

urlpatterns = [
    re_path('^videos/?$', VideoViewSet.as_view({'get':'retrieve_videos'}), name='retrieve-videos'),
]