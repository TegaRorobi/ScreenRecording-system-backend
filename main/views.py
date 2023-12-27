
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status, decorators
from django.http import Http404, FileResponse

from .serializers import *
from .models import *
from conf.utils import *
from django.conf import settings

from drf_yasg.utils import swagger_auto_schema

import pika, json


__all__ = 'VideoViewSet',


class VideoViewSet(GenericViewSet):

    def get_queryset(self):
        return Video.objects.all()

    def get_serializer_class(self):
        if self.action == 'append_video':
            return VideoChunkSerializer
        return VideoSerializer

    pagination_class = PaginatorGenerator()()

    def enqueue_video_append(self, *, queue_name:str, message:str):
        connection_parameters = pika.ConnectionParameters('localhost')
        connection = pika.BlockingConnection(connection_parameters)
        channel = connection.channel()
        channel.queue_declare(queue=queue_name)
        channel.basic_publish(exchange='', routing_key=queue_name, body=message)
        connection.close()


    @decorators.action(detail=False)
    @swagger_auto_schema(
        tags=['API Endpoints'],
        operation_summary=('API Endpoint to retrieve a paginated response of all videos')
    )
    def retrieve_videos(self, request, *args, **kwargs):
        videos = self.get_queryset()
        page = self.paginate_queryset(videos)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(videos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @decorators.action(detail=True)
    @swagger_auto_schema(
        tags=['API Endpoints'],
        operation_summary=('API Endpoint to create a new video')
    )
    def create_video(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @decorators.action(detail=True)
    @swagger_auto_schema(
        tags=['API Endpoints'],
        operation_summary=('API Endpoint to retrieve the details of a specific video retrieved by UUID')
    )
    def retrieve_video(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404:
            return Response({
                'error': f'Invalid {self.lookup_url_kwarg or self.lookup_field}. Video with '
                         f"{self.lookup_field} {kwargs.get('pk')!r} does not exist."
            }, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @decorators.action(detail=True)
    @swagger_auto_schema(
        tags=['API Endpoints'],
        operation_summary=('API Endpoint to append to an existing video retrieved by UUID')
    )
    def append_video(self, request, *args, **kwargs):

        try:
            video = self.get_object()
        except Http404:
            return Response({
                'error': f'Invalid {self.lookup_url_kwarg or self.lookup_field}. Video with '
                         f"{self.lookup_field} {kwargs.get('pk')!r} does not exist."
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            chunk = serializer.save(video=video)

            if not video.video_file:
                video.video_file.save(f'{video.id}.mp4', chunk.chunk_file)

            else:
                chunk_file_path = str(settings.BASE_DIR) + chunk.chunk_file.url
                message = {
                    'video_pk': str(video.pk),
                    'chunk_file_path': chunk_file_path
                }
                self.enqueue_video_append(queue_name='append_video', message=json.dumps(message))
                print('Successfully enqueued:', json.dumps(message, indent=4))

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @decorators.action(detail=True)
    @swagger_auto_schema(
        tags=['API Endpoints'],
        operation_summary=('API Endpoint to stream out a specific video retrieved by UUID')
    )
    def stream_video(self, request, *args, **kwargs):
        try:
            video = self.get_object()
        except Http404:
            return Response({
                'error': f'Invalid {self.lookup_url_kwarg or self.lookup_field}. Video with '
                         f"{self.lookup_field} {kwargs.get('pk')!r} does not exist."
            }, status=status.HTTP_404_NOT_FOUND)

        chunk_generator = (chunk.chunk_file.read() for chunk in video.chunks.all())

        response = FileResponse(chunk_generator, content_type='video/mp4')
        response['Content-Disposition'] = f'inline; filename="{video.title}.mp4"'
        return response


    @decorators.action(detail=True)
    @swagger_auto_schema(
        tags=['API Endpoints'],
        operation_summary=('API Endpoint to update all writeable fields of a specific video retrieved by UUID')
    )
    def update_video(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404:
            return Response({
                'error': f'Invalid {self.lookup_url_kwarg or self.lookup_field}. Video with '
                         f"{self.lookup_field} {kwargs.get('pk')!r} does not exist."
            }, status=status.HTTP_404_NOT_FOUND)
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @decorators.action(detail=True)
    @swagger_auto_schema(
        tags=['API Endpoints'],
        operation_summary=('API Endpoint to update some writeable fields of a specific video retrieved by UUID')
    )
    def partial_update_video(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update_video(request, *args, **kwargs)


    @decorators.action(detail=True)
    @swagger_auto_schema(
        tags=['API Endpoints'],
        operation_summary=('API Endpoint to delete a specific video retrieved by UUID')
    )
    def delete_video(self, request, *args, **kwargs):
        try:
            self.get_object().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Http404:
            return Response({
                'error': f'Invalid {self.lookup_url_kwarg or self.lookup_field}. Video with '
                         f"{self.lookup_field} {kwargs.get('pk')!r} does not exist."
            }, status=status.HTTP_404_NOT_FOUND)
