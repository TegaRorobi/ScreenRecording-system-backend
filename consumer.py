
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf.settings')

from conf.wsgi import get_wsgi_application
get_wsgi_application()

from main.models import *
from django.conf import settings

import pika, json, tempfile
from moviepy.editor import AudioFileClip, VideoFileClip, concatenate_videoclips

import requests


TEMPFILE_DIR = settings.BASE_DIR / 'temp'
try:
    os.mkdir(TEMPFILE_DIR)
except FileExistsError:
    pass

def transcribe_audio(audio_tempfile_path):
    endpoint = 'https://api.openai.com/v1/audio/translations'
    headers = {'Authorization': f'Bearer {settings.OPENAI_API_KEY}'}
    data = {'model': 'whisper-1'}
    files = {'file': open(audio_tempfile_path, 'rb')}
    response = requests.post(endpoint, data=data, files=files, headers=headers)
    print(response, response.json(), sep='\n')
    if hasattr(response, 'json'):
        return response.json().get('text')


def dequeue_append_video(channel, method, properties, body):
    try:
        message = json.loads(body)
        print(f'Received a message: \n{json.dumps(message, indent=4)}')
        video_pk, chunk_file_path, is_first_chunk = message.values()

        video = Video.objects.get(pk=video_pk)

        audio_tempfile_path = TEMPFILE_DIR / f'audio_{video_pk}.mp3'

        if is_first_chunk:
            video.video_file.save(f'{video_pk}.mp4', open(chunk_file_path, 'rb'))
            audio_clip = AudioFileClip(chunk_file_path)
            audio_clip.write_audiofile(audio_tempfile_path)

        else:
            video_file_path = str(settings.BASE_DIR) + video.video_file.url
            with tempfile.NamedTemporaryFile(dir=TEMPFILE_DIR, delete=False, suffix='.mp4') as final_clip_tempfile:
                existing_clip = VideoFileClip(video_file_path)
                new_clip = VideoFileClip(chunk_file_path)

                final_clip = concatenate_videoclips([existing_clip, new_clip])
                final_clip_tempfile_path = final_clip_tempfile.name

                final_clip.write_videofile(
                    final_clip_tempfile_path,
                    temp_audiofile=audio_tempfile_path,
                    remove_temp=False,
                )

                final_clip_tempfile.seek(0)
                if os.path.exists(video_file_path):
                    os.remove(video_file_path)
                video.video_file.save(f'{video_pk}.mp4', final_clip_tempfile)

                final_clip_tempfile.close()
                del existing_clip, new_clip, final_clip, final_clip_tempfile
                if os.path.exists(final_clip_tempfile_path):
                    os.remove(final_clip_tempfile_path)

        print('Getting a transcription...')
        transcription = transcribe_audio(audio_tempfile_path)
        if not transcription:
            print('Transcription not found.')
            return
        video.transcription = transcription
        video.save()
        print('Transcription successfully updated.')
        if os.path.exists(audio_tempfile_path):
            os.remove(audio_tempfile_path)

    except Exception as e:
        print(f"An error occurred during message processing: \n{'-'*44}\n\n {e}\n\n")


def create_rabbitmq_connection():
    while True:
        try:
            parameters = pika.ConnectionParameters('localhost')
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            channel.queue_declare('append_video')
            channel.basic_consume(queue='append_video', auto_ack=True, on_message_callback=dequeue_append_video)
            print('Awaiting messages to consume on the \'append_video\' queue... To exit, press CTRL+C.')
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Connection to RabbitMQ failed: {e}. Retrying...")


if __name__ == '__main__':
    create_rabbitmq_connection()
