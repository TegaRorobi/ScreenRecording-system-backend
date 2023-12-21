from django.contrib import admin
from .models import Video

# Register your models here.
@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
	class Meta:
		model = Video 
		list_display = 'title', 'video_file', 'upload_date', 'last_modified'
