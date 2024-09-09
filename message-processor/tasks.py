import os
import re
import time
import yaml
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from redis import Redis
from rq import Queue
import speech_recognition as sr
from pydub import AudioSegment
from vosk import Model, KaldiRecognizer, SetLogLevel
import json
import wave

SetLogLevel(-1)

def sanitize_title(title, max_length=50):
    """Sanitize the title to be filesystem safe, limit its length, and allow only alphanumeric characters."""
    # Replace any character that is not a letter or a number with a hyphen
    sanitized = re.sub(r'[^a-zA-Z0-9]', '-', title)
    # Replace multiple hyphens with a single hyphen
    sanitized = re.sub(r'-+', '-', sanitized)
    # Trim leading or trailing hyphens
    sanitized = sanitized.strip('-')
    return sanitized[:max_length]

# Load the configuration
with open("config.yaml", 'r') as stream:
    config = yaml.safe_load(stream)

AUDIO_FRAGMENT_LENGTH = config['audio_fragment_length']
TRANSCRIPTION_CHECK_INTERVAL = config['transcription_check_interval']
TRANSCRIPTION_MAX_WAIT_TIME = config['transcription_max_wait_time']

redis_conn = Redis(host='redis', port=6379)
q = Queue('podcast_queue', connection=redis_conn)

model_path = "vosk-model-small-en-us-0.15"
model = Model(model_path)

def audio_fragment_saved(json_string):
    item_dict = json.loads(json_string)
    audio_path = item_dict['path']
    transcript_path = item_dict['transcript_path']
    recognizer = sr.Recognizer()

    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)

    rec = KaldiRecognizer(model, 16000)
    rec.AcceptWaveform(audio_data.get_wav_data())

    result = json.loads(rec.Result())
    transcription = result.get('text', '')

    with open(transcript_path, 'w') as file:
        file.write(transcription)

    print(f"Transcription saved: {transcript_path}")

def audio_file_downloaded(json_string):
    item_dict = json.loads(json_string)
    full_length_path = item_dict['files']['full_length']

    print(f"Processing full length audio file: {full_length_path}")

    audio = AudioSegment.from_mp3(full_length_path).set_frame_rate(16000)
    duration = len(audio) // 1000

    print(f"Audio duration (seconds): {duration}")

    item_dict['files']['fragments'] = []
    fragment_length = AUDIO_FRAGMENT_LENGTH * 1000

    for i, start in enumerate(range(0, len(audio), fragment_length)):
        end = min(start + fragment_length, len(audio))
        fragment = audio[start:end]
        fragment_path = f"{os.path.splitext(full_length_path)[0]}_{start // 1000}_{end // 1000}.wav"
        fragment.export(fragment_path, format="wav")
        print(f"Created fragment: {fragment_path}")
        fragment_metadata = {
            'index': i + 1, 
            'start': start // 1000, 
            'end': end // 1000, 
            'path': fragment_path,
            'transcript_path': f"{fragment_path}.txt"
        }
        q.enqueue('tasks.audio_fragment_saved', json.dumps(fragment_metadata))
        item_dict['files']['fragments'].append(fragment_metadata)

    json_output = json.dumps(item_dict)
    q.enqueue('tasks.audio_fragment_list_enqueued', json_output)


def audio_fragment_list_enqueued(json_string):
    item_dict = json.loads(json_string)
    expected_files = [fragment['transcript_path'] for fragment in item_dict['files']['fragments']]
    start_time = time.time()

    while True:
        all_files_exist = all(os.path.exists(file) for file in expected_files)
        if all_files_exist:
            print(f"All transcription files found")
            q.enqueue('tasks.fragment_list_completed', json_string)
            break
        elif time.time() - start_time > TRANSCRIPTION_MAX_WAIT_TIME:
            print(f"Timeout occurred after waiting for {TRANSCRIPTION_MAX_WAIT_TIME} seconds.")
            break
        else:
            print(f"Waiting for transcription files. Checking again in {TRANSCRIPTION_CHECK_INTERVAL} seconds.")
            time.sleep(TRANSCRIPTION_CHECK_INTERVAL)

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
