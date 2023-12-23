
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status, decorators
from .serializers import *
from .models import *

__all__ = 'VideoViewSet',

class VideoViewSet(GenericViewSet):

    def get_queryset(self):
        if self.action == 'retrieve_videos':
            return Video.objects.all()
    def get_serializer_class(self):
        if self.action == 'retrieve_videos':
            return VideoSerializer
    pagination_class = PageNumberPagination

    @decorators.action(detail=False)
    def retrieve_videos(self, request, *args, **kwargs):
        videos = self.get_queryset()
        page = self.paginate_queryset(videos)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(videos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @decorators.action(detail=True)
    def create_video(self, request, *args, **kwargs):
        pass

    @decorators.action(detail=True)
    def append_video(self, request, *args, **kwargs):
        pass

    @decorators.action(detail=True)
    def stream_video(self, request, *args, **kwargs):
        pass

    @decorators.action(detail=True)
    def delete_video(self, request, *args, **kwargs):
        pass
