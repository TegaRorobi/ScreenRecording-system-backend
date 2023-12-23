from django.contrib import admin
from .models import Video, VideoChunk

class VideoAdmin(admin.ModelAdmin):
    list_display = 'id', 'title', 'datetime_created'
    search_fields = 'title', 'description'
    list_filter = 'datetime_created',
admin.site.register(Video, VideoAdmin)

class VideoChunkAdmin(admin.ModelAdmin):
    list_display = 'id', '_video', 'chunk_number'
    search_fields = 'video', 'chunk_number'
    list_filter = 'datetime_created',
    @admin.display()
    def _video(self):
        return self.video.__str__()
admin.site.register(VideoChunk, VideoChunkAdmin)
