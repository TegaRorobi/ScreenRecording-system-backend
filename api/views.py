
from .serializers import VideoSerializer
from main.models import Video

from rest_framework.viewsets import ModelViewSet
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from django.http import StreamingHttpResponse
from django.core.files.base import ContentFile
from django.conf import settings
from moviepy.editor import VideoFileClip, concatenate_videoclips
import os, tempfile
import whisper


class VideoViewSet(ModelViewSet):
	"""
	Viewset that allows list, create, read, update and delete 
	functionality on the Video model.
	"""
	queryset = Video.objects.all()
	serializer_class = VideoSerializer
	parser_classes = FileUploadParser,

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.model = whisper.load_model("base")

	def clean(self, *filepaths):
		for filepath in filepaths:
			os.remove(filepath)

	def retrieve(self, request, *args, **kwargs):
		try:
			video = self.get_object()
			video_path = settings.BASE_DIR.__str__() + video.video_file.url

			def file_iterator(file_path, chunk_size=1024*1024):
				with open(file_path, 'rb') as video_file:
					while True:
						chunk = video_file.read(chunk_size)
						if not chunk: 
							break
						yield chunk

			response = StreamingHttpResponse(file_iterator(video_path), status=HTTP_200_OK)
			response['Content-Type'] = 'video/mp4'
			response['Content-Disposition'] = f"inline; filename=\"{video_path.split('/')[-1]}\""
			return response

		except Video.DoesNotExist:
			return Response({'message':'Video object not found.'}, status=HTTP_400_BAD_REQUEST)

	@action(methods=['post'], detail=True)
	def append_video_data(self, request, *args, **kwargs):
		video = self.get_object()
		video_filename = f'video_{video.id}.mp4'

		new_video_data = request.body or request.POST.get('video_data')
		if not new_video_data:
			return Response({'error':'No video data provided via the \'video_data\' request parameter'}, status=HTTP_400_BAD_REQUEST)

		if not video.video_file:
			"This is the first update to the blank video file"

			video.video_file.save(video_filename, ContentFile(new_video_data))
			return Response({'message':f'Video data successfully written to {video_filename}'}, status=HTTP_200_OK)


		else:
			"This is an update to the existing video file"

			existing_video_data = video.video_file.read()

			with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as existing_tempfile:
				existing_tempfile.write(existing_video_data)
				existing_tempfile_path = existing_tempfile.name
				existing_clip = VideoFileClip(existing_tempfile_path)

			with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as new_tempfile:
				new_tempfile.write(new_video_data)
				new_tempfile_path = new_tempfile.name
				new_clip = VideoFileClip(new_tempfile_path)

			with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as final_tempfile:
				final_tempfile_path = final_tempfile.name
				final_clip = concatenate_videoclips([existing_clip, new_clip])
				final_clip.write_videofile(final_tempfile_path.name, codec='mp4')

			with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as audio_tempfile:
				audio_clip = final_clip.audio
				audio_clip.write_audiofile(audio_tempfile.name, codec='mp3')
				audio_tempfile_path = audio_tempfile.name

			final_video_data = open(final_tempfile_path, 'rb').read()
			final_video_file = ContentFile(final_video_data)
			video.file.save(f'video_{video.id}.mp4', final_video_file)

			transcription = self.model.transcribe(audio_tempfile_path)
			video.transcription = transcription['text']
			video.save()

			self.clean(existing_tempfile_path, new_tempfile_path, final_tempfile_path)
			return Response({'message':f'Video data successfully appended to {video_filename}'}, status=HTTP_200_OK)

