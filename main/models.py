
from django.db import models
import uuid

__all__ = 'Video', 'VideoChunk'

class Video(models.Model):
    id = models.UUIDField(default=uuid.uuid4(), primary_key=True, null=False, unique=True, editable=False)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    video_file = models.FileField(upload_to='videos/', null=True, blank=True)
    transcription = models.TextField(null=True, blank=True)
    # timestamps
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-datetime_created',)

    def __str__(self):
        return self.title or self.file.url


class VideoChunk(models.Model):
    id = models.UUIDField(default=uuid.uuid4(), primary_key=True, null=False, unique=True, editable=False)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='chunks')
    chunk_file = models.FileField(upload_to='video_chunks/', null=True, blank=True)
    chunk_number = models.IntegerField()
    # timestamps
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-datetime_created',)

    def __str__(self):
        return f'Chunk {self.chunk_number}: {self.video}'
