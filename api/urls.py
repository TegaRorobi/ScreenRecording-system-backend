from django.urls import path 
from .views import VideoViewSet

app_name = 'api'
urlpatterns = [
	path(
		'videos/<int:pk>/', 
		VideoViewSet.as_view({
			'get':'retrieve',
			'put':'update',
			'patch':'partial_update',
			'delete':'destroy'})), 

	path(
		'videos/list/', 
		VideoViewSet.as_view({'get':'list'})),

	path(
		'videos/create/', 
		VideoViewSet.as_view({'post':'create'})),

	path(
		'videos/<int:pk>/append/', 
		VideoViewSet.as_view({'post':'append_video_data'})), 
]
