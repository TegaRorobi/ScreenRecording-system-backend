
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status, decorators
from django.http import Http404, FileResponse

from .serializers import *
from .models import *
from conf.utils import *
from django.conf import settings

import tempfile, os
from moviepy.editor import VideoFileClip, concatenate_videoclips


__all__ = 'VideoViewSet',


class VideoViewSet(GenericViewSet):

    def get_queryset(self):
        return Video.objects.all()

    def get_serializer_class(self):
        if self.action in ('retrieve_videos', 'create_video', 'update_video'):
            return VideoSerializer
        elif self.action == 'append_video':
            return VideoChunkSerializer

    pagination_class = PaginatorGenerator()()

    def remove_paths(self, *filepaths):
        for fpath in filepaths:
            os.remove(fpath)


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

        try:
            video = self.get_object()
        except Http404:
            return Response({
                'error': f'Invalid {self.lookup_url_kwarg or self.lookup_field}. Video with '
                         f"{self.lookup_field} {kwargs.get('pk')!r} does not exist."
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(video=video)
            chunk_file = serializer.validated_data['chunk_file']
            video_filename = f'{video.id}.mp4'

            if not video.video_file:
                video.video_file.save(video_filename, chunk_file)

            else:
                existing_clip_tempfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
                existing_clip_tempfile.write(video.video_file.read())
                existing_clip_tempfile.seek(0)
                existing_clip_tempfile_path = existing_clip_tempfile.name
                existing_clip = VideoFileClip(existing_clip_tempfile_path)
                # print(existing_clip_tempfile, existing_clip_tempfile_path, existing_clip, '\n\n', sep='\n')

                new_clip_tempfile =  tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
                new_clip_tempfile.write(chunk_file.read())
                new_clip_tempfile.seek(0)
                new_clip_tempfile_path = new_clip_tempfile.name
                new_clip = VideoFileClip(new_clip_tempfile_path)
                # print(new_clip_tempfile, new_clip_tempfile_path, new_clip, '\n\n', sep='\n')

                final_clip_tempfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
                final_clip = concatenate_videoclips([existing_clip, new_clip])
                final_clip_tempfile_path = final_clip_tempfile.name
                final_clip.write_videofile(final_clip_tempfile_path)
                # print(final_clip_tempfile, final_clip_tempfile.name, final_clip, '\n\n', sep='\n')

                final_clip_tempfile.seek(0)
                video.video_file.save(video_filename, final_clip_tempfile)

                self.remove_paths(existing_clip_tempfile_path, new_clip_tempfile_path, final_clip_tempfile_path)

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @decorators.action(detail=True)
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
    def partial_update_video(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update_video(request, *args, **kwargs)


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
