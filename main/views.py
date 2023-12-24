
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status, decorators
from django.http import Http404
from .serializers import *
from .models import *
from conf.utils import *

__all__ = 'VideoViewSet',

class VideoViewSet(GenericViewSet):

    def get_queryset(self):
        return Video.objects.all()
    def get_serializer_class(self):
        if self.action in ('retrieve_videos', 'create_video'):
            return VideoSerializer
    pagination_class = PaginatorGenerator()()

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
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @decorators.action(detail=True)
    def append_video(self, request, *args, **kwargs):
        pass

    @decorators.action(detail=True)
    def stream_video(self, request, *args, **kwargs):
        pass

    @decorators.action(detail=True)
    def delete_video(self, request, *args, **kwargs):
        try:
            self.get_object().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Http404:
            return Response({
                'error': f'Invalid {self.lookup_url_kwarg or self.lookup_field}. Video with '
                         f"{self.lookup_field} {kwargs.get('pk')!r} does not exist."
            }, status=status.HTTP_404_NOT_FOUND)
