import requests
from bs4 import BeautifulSoup
import argparse
import re
import os

def fetch_audio_url(rss_url, episode_number=None):
    # Fetch the RSS feed
    response = requests.get(rss_url)
    rss_content = response.content

    # Parse the RSS feed
    soup = BeautifulSoup(rss_content, 'xml')
    items = soup.find_all('item')

    # Extract audio URLs
    audio_urls = {}
    for item in items:
        title = item.find('title').text
        match = re.search(r'Ep (\d+)', title)
        if match:
            ep_number = int(match.group(1))
            enclosure = item.find('enclosure')
            if enclosure and enclosure.get('type') == 'audio/mpeg':
                audio_urls[ep_number] = enclosure['url']

    if episode_number:
        return audio_urls.get(episode_number), episode_number
    else:
        latest_episode_number = max(audio_urls.keys(), default=None)
        return audio_urls.get(latest_episode_number), latest_episode_number

def download_episode(audio_url, episode_number, download_folder="data"):
    # Create a directory named after the episode number inside the download folder
    episode_folder = os.path.join(download_folder, str(episode_number))
    os.makedirs(episode_folder, exist_ok=True)
    # Get the original file name
    filename = os.path.basename(audio_url)
    download_path = os.path.join(episode_folder, filename)
    
    # Download the audio file
    response = requests.get(audio_url, stream=True)
    if response.status_code == 200:
        with open(download_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
        print(f"Episode downloaded successfully: {download_path}")
    else:
        print(f"Failed to download episode. Status code: {response.status_code}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and download audio URL from an RSS feed")
    parser.add_argument('rss_url', type=str, help='URL of the RSS feed')
    parser.add_argument('--episode', type=int, help='Episode number to fetch', default=None)
    args = parser.parse_args()

    audio_url, episode_number = fetch_audio_url(args.rss_url, args.episode)

    if audio_url:
        print(f"Audio URL: {audio_url}")
        download_episode(audio_url, episode_number, 'data')
    else:
        print(f"Episode {args.episode} not found." if args.episode else "No episodes found.")