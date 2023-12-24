
from django.urls import re_path
from .views import *

app_name = 'main'

urlpatterns = [
    re_path(
        '^videos/?$',
        VideoViewSet.as_view({
            'get':'retrieve_videos',
            'post': 'create_video'
        }),
        name='retrieve-create-videos'
    ),

    re_path(
        '^videos/(?P<pk>[a-zA-Z0-9\-]+)/?$',
        VideoViewSet.as_view({
            'delete':'delete_video',
        }),
        name='delete-video'
    ),
]