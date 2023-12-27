
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf.settings')

from conf.wsgi import get_wsgi_application
get_wsgi_application()

from main.models import *
from django.conf import settings

import pika, json, tempfile
from moviepy.editor import VideoFileClip, concatenate_videoclips

TEMPFILE_DIR = settings.BASE_DIR / 'temp'
try:
    os.mkdir(TEMPFILE_DIR)
except FileExistsError:
    pass

def dequeue_append_video(channel, method, properties, body):
    try:
        message = json.loads(body)
        print(f'Received a message: \n{json.dumps(message, indent=4)}')
        video_pk, chunk_file_path = message.values()

        video = Video.objects.get(pk=video_pk)
        video_file_path = str(settings.BASE_DIR) + video.video_file.url

        with tempfile.NamedTemporaryFile(dir=TEMPFILE_DIR, delete=False, suffix='.mp4') as final_clip_tempfile:
            print(video_file_path, chunk_file_path)
            existing_clip = VideoFileClip(video_file_path)
            new_clip = VideoFileClip(chunk_file_path)

            final_clip = concatenate_videoclips([existing_clip, new_clip])
            final_clip_tempfile_path = final_clip_tempfile.name
            final_clip.write_videofile(final_clip_tempfile_path)

            final_clip_tempfile.seek(0)
            os.remove(video_file_path)
            video.video_file.save(f'{video_pk}.mp4', final_clip_tempfile)

            final_clip_tempfile.close()
            del existing_clip, new_clip, final_clip, final_clip_tempfile
            os.remove(final_clip_tempfile_path)

    except Exception as e:
        print(f"An error occurred during message processing: \n{'-'*44}\n\n {e}")

def create_rabbitmq_connection():
    while True:
        try:
            parameters = pika.ConnectionParameters('localhost')
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            channel.queue_declare('append_video')
            channel.basic_consume(queue='append_video', auto_ack=True, on_message_callback=dequeue_append_video)
            print('Consuming started on queue \'append_video\'...')
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Connection to RabbitMQ failed: {e}. Retrying...")


if __name__ == '__main__':
    create_rabbitmq_connection()
