import os
import re
import requests
from bs4 import BeautifulSoup
from pydub import AudioSegment
from redis import Redis
from rq import Queue

# Load the configuration
import yaml

with open("config.yaml", 'r') as stream:
    config = yaml.safe_load(stream)

AUDIO_FRAGMENT_LENGTH = config['audio_fragment_length']

redis_conn = Redis(host='redis', port=6379)
q = Queue(connection=redis_conn)

def process_episode_item(item_xml):
    soup = BeautifulSoup(item_xml, 'xml')
    item = soup.find('item')
    
    title = item.find('title').text
    enclosure = item.find('enclosure')
    audio_url = enclosure['url'] if enclosure else None

    if not audio_url:
        print("Audio URL not found in the item.")
        return

    episode_number_match = re.search(r'Ep (\d+)', title)
    episode_number = episode_number_match.group(1) if episode_number_match else "unknown"

    download_folder = "/data"
    episode_folder = os.path.join(download_folder, episode_number)
    os.makedirs(episode_folder, exist_ok=True)
    
    filename = os.path.basename(audio_url)
    download_path = os.path.join(episode_folder, filename)
    
    response = requests.get(audio_url, stream=True)
    if response.status_code == 200:
        with open(download_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
        print(f"Episode downloaded successfully: {download_path}")
        
        # Append the full length file to the item XML
        files_tag = soup.new_tag('files')
        full_length_tag = soup.new_tag('full_length')
        full_length_tag.string = download_path
        files_tag.append(full_length_tag)
        item.append(files_tag)

        # Enqueue the task to process the local audio
        item_xml = str(soup)
        q.enqueue('tasks.process_local_audio', item_xml)
    else:
        print(f"Failed to download episode. Status code: {response.status_code}")

def process_local_audio(item_xml):
    soup = BeautifulSoup(item_xml, 'xml')
    item = soup.find('item')
    files = item.find('files')
    full_length_path = files.find('full_length').text

    print(f"Processing full length audio file: {full_length_path}")  # Debug statement

    # Load the full length audio file
    audio = AudioSegment.from_mp3(full_length_path)
    duration = len(audio) // 1000  # duration in seconds
    print(f"Audio duration (seconds): {duration}")  # Debug statement

    fragments_tag = soup.new_tag('fragments')
    fragment_length = AUDIO_FRAGMENT_LENGTH * 1000  # length in milliseconds

    for i, start in enumerate(range(0, len(audio), fragment_length)):
        end = min(start + fragment_length, len(audio))
        fragment = audio[start:end]
        fragment_filename = f"{os.path.splitext(full_length_path)[0]}_{start // 1000}_{end // 1000}.mp3"
        fragment.export(fragment_filename, format="mp3")
        print(f"Created fragment: {fragment_filename}")  # Debug statement

        # Append the fragment details to the XML
        fragment_tag = soup.new_tag('fragment', index=str(i + 1), start=str(start // 1000), end=str(end // 1000))
        fragment_tag.string = fragment_filename
        fragments_tag.append(fragment_tag)

    files.append(fragments_tag)

    # Save the updated item XML
    item_xml_updated = str(soup)
    # You can save this updated XML to a file or process it further as needed
    print(f"Updated item XML: {item_xml_updated}")  # Debug statement