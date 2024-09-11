from lib.status import update_job_status
import json
from lib.queue import q

class Events:
    @staticmethod
    def fire(event_type, dic_data):
        
        if not 'job_id' in dic_data:
            print(f"Event fired without job_id: {event_type}")
            return

        job_id = dic_data['job_id']
        print(f"Event fired: {event_type} for job {job_id}")

        if event_type == 'rss_feed_item_found':
            update_job_status(job_id, 'rss_item_located', progress='10%')
            Events.enqueue_next_task('web.media_download_requested', dic_data)
        elif event_type == 'media_downloading':
            update_job_status(job_id, 'media_downloading')
        elif event_type == 'media_download_completed':
            update_job_status(job_id, 'media_download_completed', progress='12%')
            Events.enqueue_next_task('media.new_file_present', dic_data)
        elif event_type == 'fragments_created':
            Events.enqueue_next_task('pending.file_list_enqueued', dic_data)
            for fragment in dic_data['files']['fragments']:
                Events.enqueue_next_task('audio.fragment_saved', fragment)
            update_job_status(job_id, 'transcription_started', progress='20%')
        elif event_type == 'transcription_in_progress':
            ratio = dic_data.get('progress', 0)
            progress = 20 + (75 * ratio) 
            print(f'transcription_in_progress: {progress:.2f}%')
            update_job_status(job_id, 'transcription_in_progress', progress=f'{progress:.2f}%')
        elif event_type == 'transcription_fragments_created':
            update_job_status(job_id, 'transcription_progess', progress='95%')
            Events.enqueue_next_task('file.fragment_list_completed', dic_data)
        elif event_type == 'transcript_file_saved':
            transcript_file_path = dic_data['files']['transcript_file_path']
            update_job_status(job_id, 'transcript_ready', progress='100%', details=transcript_file_path)
    @classmethod
    def enqueue_next_task(cls, task, dic_data):
        json_output = json.dumps(dic_data)
        q.enqueue(task, json_output)