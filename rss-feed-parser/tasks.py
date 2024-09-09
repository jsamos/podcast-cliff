import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from redis import Redis
from rq import Queue
import xmltodict
import json


redis_conn = Redis(host='redis', port=6379)
q = Queue('rss_queue', connection=redis_conn)
podcast_queue = Queue('podcast_queue', connection=redis_conn)

def create_episode_folder(folder):
    download_folder = "/data"
    episode_folder = os.path.join(download_folder, folder)
    os.makedirs(episode_folder, exist_ok=True)
    return episode_folder

def save_episode(response, path):
    with open(path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)
    print(f"Episode downloaded successfully: {path}")

def process_episode_item(json_string):
    item_dict = json.loads(json_string)
    audio_url = item_dict['url']

    if not audio_url:
        print("Audio URL not found in the item.")
        return

    filename = os.path.basename(urlparse(audio_url).path)
    episode_folder = create_episode_folder(filename[:-4])
    download_path = os.path.join(episode_folder, filename)
    response = requests.get(audio_url, stream=True)

    if response.status_code != 200:
        print(f"Failed to download episode. Status code: {response.status_code}")
    else:
        save_episode(response, download_path)
        item_dict['files'] = {'full_length': download_path}
        print(item_dict)
        json_output = json.dumps(item_dict)
        podcast_queue.enqueue('tasks.audio_file_downloaded', json_output)