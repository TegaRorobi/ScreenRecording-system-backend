# Api Documentation  

## Model overview  
The **Video** model possesses the following fields:
- `title` : Nullable Character field, expresses the title of the video
- `description` : Nullable Character field, expresses the description of the video
- `video_file` : Nullable File field, contains the actual mp4 data of the video
- `transcription` : Nullable Character field, contains the text transcription of the video
- `upload_date` : Non-nullable DateTime field, contains the instantiation time of the video
- `last_modified` : Non-nullable DateTime field, contains the last modification time of the video

<br/><br/>

## Endpoints  
- GET `/api/videos/list/` : List out all videos. This endpoint returns JSON data of all saved video instances.
  <br/>
- POST `/api/videos/create/` : Create a video. This endpoint accepts common video parameters and creates a new video instance, returning the data of the instance.
  <br/>
- POST `/api/videos/<int:pk>/append/` : Append data to an existing video. This endpoint accepst a `video_data` request parameter and appends the data to the existing video's data file, refreshes the transcription and saves the video instance.
  <br/>
- GET `/api/videos/<int:pk>/` : Retrieve a particular video by pk (id). This endpoint returns a _StreamingHttpResponse_ which streams out the video file 1MiB at a time via a generator.
  <br/>
- PUT `/api/videos/<int:pk>/` : Update all writeable fields of a Video instance.
  <br/>
- PATCH `/api/videos/<int:pk>/` : Update selected writeable fields of a Video instance.
  <br/>
- DELETE `/api/videos/<int:pk>/` : Delete a Video instance.

<br/><br/>

## Endpoint details
#### POST `/api/videos/<int:pk>/append/`
This endpoint accepts a `video_data` request parameter. If the targeted video instance contains
existing video data, a tempfile is created to store that existing data, another is created to store the new incoming data, and video clips
are produced from these tempfiles. These clips are then concatenated with the _concatenate_videoclips_ function from the _moviepy_ module.
This merged clip's data is extracted and saved to a final tempfile, and then the data in this file is used to overwrite the `video_file` field 
of the video instance. A new transcription of this merged clip's data is created and written to the instance's `transcription` field and the instance is saved.
In the case where the targeted video file does not contain existing video data, the data is saved directly to the `video_file` field of the
instance and a transcription generated.  

#### GET `/api/videos/<int:pk>/`
This endpoint retrieves a particular video instance by the _pk_ parameter. The instance is retrieved and then a generator is created to
read out 1MiB (2^11 bytes) of data on every call to the next() method of the generator. This generator is then passed to the StreamingHttpResponse
class from django and then some metadata are configured and then the data is returned. 

<br/><br/>

## Tools/modules used
- django
- djangorestframework
- moviepy
- openai-whisper

<br/><br/>

## Other
The project also has some django-rendered pages to allow for video play (`/play/<int:pk>/`), listing out all videos (`/list/`)
and also uploading videos (`/upload/`).  
Disclaimer: The project may possess bugs.
