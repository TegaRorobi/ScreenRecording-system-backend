
from django.urls import re_path
from .views import *

app_name = 'main'

urlpatterns = [
    re_path('^videos/?$', VideoViewSet.as_view({'get':'retrieve_videos'}), name='retrieve-videos'),
    re_path('^videos/create/?$', VideoViewSet.as_view({'post':'create_video'}), name='create-video'),
]