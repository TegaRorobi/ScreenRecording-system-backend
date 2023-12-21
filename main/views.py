from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from django.views.generic import View
from django.http import JsonResponse
from .forms import VideoForm
from .models import Video


# Create your views here.
class VideoUploadView(View):

	@csrf_exempt
	def get(self, request, *args, **kwargs):
		form = VideoForm()
		return render(request, 'upload.html', context={'form':form})

	@csrf_exempt
	def post(self, request, *args, **kwargs):
		form = VideoForm(request.POST, request.FILES)
		if form.is_valid():
			form.save()
			return redirect('video-list')
		return JsonResponse({'message':'Invalid input❌'}, status=400)

class VideoListView(View):
	def get(self, request, *args, **kwargs):
		videos = Video.objects.all()
		return render(request, 'list.html', context={'videos':videos})

class VideoPlayView(View):
	def get(self, request, pk, *args, **kwargs):
		video = get_object_or_404(Video, pk=pk)
		return render(request, 'play.html', context={'video':video})

def get_csrf_token(request):
	return JsonResponse({'csrf_token':get_token(request)}, status=200)