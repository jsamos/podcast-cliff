import requests
from bs4 import BeautifulSoup
import argparse
import re
import os

def fetch_podcast_rss(rss_url):
    # Fetch the RSS feed
    response = requests.get(rss_url)
    response.raise_for_status()  # Ensure we notice bad responses
    return BeautifulSoup(response.content, 'xml')

def fetch_episode_item(soup, episode_number=None):
    items = soup.find_all('item')
    if episode_number:
        for item in items:
            title = item.find('title').text
            match = re.search(r'Ep (\d+)', title)
            if match and int(match.group(1)) == episode_number:
                return item
    return items[0] if items else None

def download_episode(item, download_folder="data"):
    title = item.find('title').text
    match = re.search(r'Ep (\d+)', title)
    if not match:
        print("Episode number not found in the title.")
        return

    episode_number = match.group(1)
    audio_url = item.find('enclosure')['url']
    
    # Create a directory named after the episode number inside the download folder
    episode_folder = os.path.join(download_folder, episode_number)
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

    soup = fetch_podcast_rss(args.rss_url)
    item = fetch_episode_item(soup, args.episode)

    if item:
        download_episode(item, 'data')
    else:
        print(f"Episode {args.episode} not found." if args.episode else "No episodes found.")