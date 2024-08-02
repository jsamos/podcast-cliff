import requests
import os
import re
from bs4 import BeautifulSoup

def process_episode_item(item_xml):
    item = BeautifulSoup(item_xml, 'xml').find('item')
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
        
        metadata = {
            "episode_number": episode_number,
            "title": title,
            "file_path": download_path
        }
        print(f"Processing metadata: {metadata}")
    else:
        print(f"Failed to download episode. Status code: {response.status_code}")