from django.urls import path 
from .views import *

urlpatterns = [
	path('upload/', VideoUploadView.as_view(), name='video-upload'),
	path('list/', VideoListView.as_view(), name='video-list'),
	path('play/<int:pk>/', VideoPlayView.as_view(), name='video-play'),

	path('get_csrf_token/', get_csrf_token, name='get-csrf-token'),
]