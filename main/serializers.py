
from rest_framework import serializers
from .models import Video, VideoChunk

__all__ = 'VideoSerializer', 'VideoChunkSerializer'

class VideoChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoChunk
        fields = '__all__'
        read_only_fields = 'id', 'video', 'datetime_created', 'datetime_updated'

class VideoSerializer(serializers.ModelSerializer):
    chunks = VideoChunkSerializer(many=True, read_only=True)
    class Meta:
        model = Video
        fields = '__all__'
        read_only_fields = 'id', 'datetime_created', 'datetime_updated'
