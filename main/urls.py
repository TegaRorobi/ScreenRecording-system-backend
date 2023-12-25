
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
        name='videos-list-create'
    ),

    re_path(
        '^videos/(?P<pk>[a-zA-Z0-9\-]+)/?$',
        VideoViewSet.as_view({
            'post':'append_video',
            'put':'update_video',
            'patch':'partial_update_video',
            'delete':'delete_video',
        }),
        name='video-detail'
    ),

    re_path(
        '^videos/(?P<pk>[a-zA-Z0-9\-]+)/stream/?$',
        VideoViewSet.as_view({
            'get': 'stream_video',
        }),
        name='video-stream'
    ),
]
