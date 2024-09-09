import os
import time
from redis import Redis
from rq import Queue
import json
from lib.transcription import transcribe_audio
from lib.audio import create_audio_fragments
from config import AUDIO_FRAGMENT_LENGTH
from lib.files import wait_for_files, add_transcript_path

redis_conn = Redis(host='redis', port=6379)
q = Queue('podcast_queue', connection=redis_conn)

model_path = "vosk-model-small-en-us-0.15"

def audio_fragment_saved(json_string):
    item_dict = json.loads(json_string)
    transcription = transcribe_audio(item_dict['path'])

    with open(item_dict['transcript_path'], 'w') as file:
        file.write(transcription)

    print(f"Transcription saved: {item_dict['transcript_path']}")

def audio_file_downloaded(json_string):
    item_dict = json.loads(json_string)
    full_length_path = item_dict['files']['full_length']
    item_dict['files']['fragments'] = create_audio_fragments(full_length_path, AUDIO_FRAGMENT_LENGTH)
    add_transcript_path(item_dict['files']['fragments'])

    for fragment in item_dict['files']['fragments']:
        q.enqueue('tasks.audio_fragment_saved', json.dumps(fragment))

    json_output = json.dumps(item_dict)
    q.enqueue('tasks.audio_fragment_list_enqueued', json_output)

def audio_fragment_list_enqueued(json_string):
    item_dict = json.loads(json_string)
    expected_files = [fragment['transcript_path'] for fragment in item_dict['files']['fragments']]
    files_found = wait_for_files(expected_files)
    
    if files_found:
        print(f"All transcription files found")
        q.enqueue('tasks.fragment_list_completed', json_string)
    else:
        print(f"Tramscription timeout occurred.")

def fragment_list_completed(json_string):
    item_dict = json.loads(json_string)
    full_length_path = item_dict['files']['full_length']
    episode_folder = os.path.dirname(full_length_path)
    filename_without_ext = os.path.splitext(os.path.basename(full_length_path))[0]
    transcript_file_path = os.path.join(episode_folder, f"{filename_without_ext}_transcript.txt")

    with open(transcript_file_path, 'w') as transcript_file:
        for fragment in item_dict['files']['fragments']:
            start_time = fragment['start']
            end_time = fragment['end']
            transcript_file.write(f">>TIME: {start_time}, {end_time}\n")
            transcript_path = fragment['transcript_path']
            with open(transcript_path, 'r') as fragment_file:
                transcript_file.write(fragment_file.read() + "\n")

    print(f"Combined transcript saved: {transcript_file_path}")

    json_output = json.dumps(item_dict)
    q.enqueue('tasks.transcript_file_saved', json_output)

def transcript_file_saved(json_string):
    item_dict = json.loads(json_string)

    files = item_dict['files']
    full_length_path = files['full_length']
    fragments = files['fragments']
    fragment_files = [fragment['path'] for fragment in fragments]
    transcript_files = [fragment['transcript_path'] for fragment in fragments]

    for file_path in [full_length_path] + fragment_files + transcript_files:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted file: {file_path}")
        else:
            print(f"File not found, could not delete: {file_path}")

    print("All temporary files deleted, final transcript preserved.")
