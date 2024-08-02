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

def format_timestamp(timestamp):
    parts = timestamp.split(':')
    if len(parts) == 2:  # mm:ss format
        return f"00:{parts[0].zfill(2)}:{parts[1].zfill(2)}"
    elif len(parts) == 3:  # HH:mm:ss format
        return f"{parts[0].zfill(2)}:{parts[1].zfill(2)}:{parts[2].zfill(2)}"
    return timestamp

def parse_timestamps(item):
    content_encoded = item.find('content:encoded')
    if content_encoded:
        content_html = content_encoded.string
        if content_html and '<strong>Timestamps:</strong>' in content_html:
            soup = BeautifulSoup(content_html, 'html.parser')
            timestamps = []
            found_timestamps = False

            for p in soup.find_all('p'):
                text = p.get_text(strip=True)
                if text.startswith('Timestamps:'):
                    found_timestamps = True
                    continue
                if found_timestamps:
                    match = re.match(r'\((\d{1,2}:\d{2}(?::\d{2})?)\)\s*-?\s*(.*)', text)
                    if match:
                        formatted_timestamp = format_timestamp(match.group(1))
                        timestamps.append((formatted_timestamp, match.group(2)))
                    else:
                        break

            if timestamps:
                timestamps_tag = BeautifulSoup(features='xml').new_tag('timestamps')
                for ts in timestamps:
                    timestamp_tag = BeautifulSoup(features='xml').new_tag('timestamp')
                    start_tag = BeautifulSoup(features='xml').new_tag('start')
                    start_tag.string = ts[0]
                    title_tag = BeautifulSoup(features='xml').new_tag('title')
                    title_tag.string = ts[1]
                    timestamp_tag.append(start_tag)
                    timestamp_tag.append(title_tag)
                    timestamps_tag.append(timestamp_tag)
                
                item.append(timestamps_tag)

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
        parse_timestamps(item)
        download_episode(item, 'data')
    else:
        print(f"Episode {args.episode} not found." if args.episode else "No episodes found.")