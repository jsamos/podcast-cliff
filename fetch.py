import requests
from bs4 import BeautifulSoup
import argparse
import re

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
        return audio_urls.get(episode_number)
    else:
        latest_episode = max(audio_urls.keys(), default=None)
        return audio_urls.get(latest_episode)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch audio URL from an RSS feed")
    parser.add_argument('rss_url', type=str, help='URL of the RSS feed')
    parser.add_argument('--episode', type=int, help='Episode number to fetch', default=None)
    args = parser.parse_args()

    audio_url = fetch_audio_url(args.rss_url, args.episode)

    if audio_url:
        print(audio_url)
    else:
        print(f"Episode {args.episode} not found." if args.episode else "No episodes found.")