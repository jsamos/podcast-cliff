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
from vosk import Model, KaldiRecognizer
import json
import wave


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
q = Queue(connection=redis_conn)

model_path = "vosk-model-small-en-us-0.15"
model = Model(model_path)

def check_audio_file(wav_path):
    with wave.open(wav_path, 'r') as wf:
        sample_rate = wf.getframerate()
        n_frames = wf.getnframes()
        duration = n_frames / sample_rate
        print(f"Sample rate: {sample_rate}, Duration: {duration}s, Frames: {n_frames}")

def process_audio_fragment(fragment_path):
    check_audio_file(fragment_path)

    recognizer = sr.Recognizer()

    with sr.AudioFile(fragment_path) as source:
        audio_data = recognizer.record(source)

    rec = KaldiRecognizer(model, 16000)
    rec.AcceptWaveform(audio_data.get_wav_data())

    result = json.loads(rec.Result())
    transcription = result.get('text', '')

    transcription_path = f"{fragment_path}.txt"
    with open(transcription_path, 'w') as file:
        file.write(transcription)

    print(f"Transcription saved: {transcription_path}")

def process_local_audio(item_xml):
    soup = BeautifulSoup(item_xml, 'xml')
    item = soup.find('item')
    files = item.find('files')
    full_length_path = files.find('full_length').text

    print(f"Processing full length audio file: {full_length_path}")

    audio = AudioSegment.from_mp3(full_length_path).set_frame_rate(16000)
    duration = len(audio) // 1000
    print(f"Audio duration (seconds): {duration}")

    fragments_tag = soup.new_tag('fragments')
    fragment_length = AUDIO_FRAGMENT_LENGTH * 1000

    for i, start in enumerate(range(0, len(audio), fragment_length)):
        end = min(start + fragment_length, len(audio))
        fragment = audio[start:end]
        fragment_filename = f"{os.path.splitext(full_length_path)[0]}_{start // 1000}_{end // 1000}.wav"
        fragment.export(fragment_filename, format="wav")
        print(f"Created fragment: {fragment_filename}")

        q.enqueue('tasks.process_audio_fragment', fragment_filename)

        fragment_tag = soup.new_tag('fragment', index=str(i + 1), start=str(start // 1000), end=str(end // 1000))
        fragment_tag.string = fragment_filename
        fragments_tag.append(fragment_tag)

    files.append(fragments_tag)

    item_xml_updated = str(soup)
    q.enqueue('tasks.process_audio_generation_completed', item_xml_updated)
    print(f"Updated item XML: {item_xml_updated}")

def process_episode_item(item_xml):
    soup = BeautifulSoup(item_xml, 'xml')
    item = soup.find('item')

    title = item.find('title').text
    sanitized_title = sanitize_title(title)
    enclosure = item.find('enclosure')
    audio_url = enclosure['url'] if enclosure else None

    if not audio_url:
        print("Audio URL not found in the item.")
        return

    download_folder = "/data"
    episode_folder = os.path.join(download_folder, sanitized_title)
    os.makedirs(episode_folder, exist_ok=True)

    filename = os.path.basename(urlparse(audio_url).path)
    download_path = os.path.join(episode_folder, filename)

    response = requests.get(audio_url, stream=True)
    if response.status_code == 200:
        with open(download_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
        print(f"Episode downloaded successfully: {download_path}")

        files_tag = soup.new_tag('files')
        full_length_tag = soup.new_tag('full_length')
        full_length_tag.string = download_path
        files_tag.append(full_length_tag)
        item.append(files_tag)

        item_xml_updated = str(soup)
        # Assuming q.enqueue is a task queue for further processing
        q.enqueue('tasks.process_local_audio', item_xml_updated)
    else:
        print(f"Failed to download episode. Status code: {response.status_code}")

def process_audio_generation_completed(item_xml):
    soup = BeautifulSoup(item_xml, 'xml')
    item = soup.find('item')
    fragments = item.find_all('fragment')

    expected_files = [f"{fragment.string}.txt" for fragment in fragments]
    start_time = time.time()
    while True:
        all_files_exist = all(os.path.exists(file) for file in expected_files)
        if all_files_exist:
            for fragment, file in zip(fragments, expected_files):
                fragment['transcript'] = file
            print(f"All transcription files found: {expected_files}")
            q.enqueue('tasks.process_transcript_completed', str(soup))
            break
        elif time.time() - start_time > TRANSCRIPTION_MAX_WAIT_TIME:
            print(f"Timeout occurred after waiting for {TRANSCRIPTION_MAX_WAIT_TIME} seconds.")
            break
        else:
            print(f"Waiting for transcription files. Checking again in {TRANSCRIPTION_CHECK_INTERVAL} seconds.")
            time.sleep(TRANSCRIPTION_CHECK_INTERVAL)

    item_xml_updated = str(soup)
    print(f"Final item XML: {item_xml_updated}")

def process_transcript_completed(item_xml):
    soup = BeautifulSoup(item_xml, 'xml')
    item = soup.find('item')

    episode_title = item.find('title').text
    sanitized_title = sanitize_title(episode_title)

    # Determine the episode folder and transcript file path
    download_folder = "/data"

    # Use the sanitized title for folder and file names
    episode_folder = os.path.join(download_folder, sanitized_title)
    transcript_file_path = os.path.join(episode_folder, f"transcript_{sanitized_title}.txt")

    # Open the transcript file for writing
    with open(transcript_file_path, 'w') as transcript_file:
        # Write the episode summary
        content_encoded = item.find('encoded') #formerly content:encoded
        if content_encoded:
            transcript_file.write(">>Episode Summary\n")
            transcript_file.write(content_encoded.text + "\n\n")

        # Write the transcriptions for each fragment
        fragments = item.find_all('fragment')
        for fragment in fragments:
            start_time = fragment['start']
            end_time = fragment['end']
            transcript_file.write(f">>TIME: {start_time}, {end_time}\n")
            transcript_path = fragment['transcript']
            with open(transcript_path, 'r') as fragment_file:
                transcript_file.write(fragment_file.read() + "\n")

    print(f"Combined transcript saved: {transcript_file_path}")

    # Enqueue the next task
    q.enqueue('tasks.process_full_transcript_completed', str(soup))

def process_full_transcript_completed(item_xml):
    soup = BeautifulSoup(item_xml, 'xml')
    item = soup.find('item')

    # Determine the files to delete
    files = item.find('files')
    full_length_path = files.find('full_length').text

    fragments = item.find_all('fragment')
    fragment_files = [fragment.string for fragment in fragments]
    transcript_files = [fragment['transcript'] for fragment in fragments]

    # Delete the files
    for file_path in [full_length_path] + fragment_files + transcript_files:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted file: {file_path}")
        else:
            print(f"File not found, could not delete: {file_path}")

    print("All temporary files deleted, final transcript preserved.")
