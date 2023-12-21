from rest_framework import serializers 
from main.models import Video

class VideoSerializer(serializers.ModelSerializer):
	class Meta:
		model = Video 
		fields = [field.name for field in model._meta.fields]