import requests
from bs4 import BeautifulSoup
import argparse
import re
from redis import Redis
from rq import Queue
import lxml.etree as ET

redis_conn = Redis(host='redis', port=6379)
q = Queue(connection=redis_conn)

def fetch_podcast_rss(rss_url):
    response = requests.get(rss_url)
    response.raise_for_status()
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

def item_to_xml(item):
    # Extract the XML as a string with namespaces properly defined
    item_soup = BeautifulSoup(str(item), 'xml')
    return str(item_soup)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and enqueue episode item from an RSS feed")
    parser.add_argument('rss_url', type=str, help='URL of the RSS feed')
    parser.add_argument('--episode', type=int, help='Episode number to fetch', default=None)
    args = parser.parse_args()

    soup = fetch_podcast_rss(args.rss_url)
    item = fetch_episode_item(soup, args.episode)

    if item:
        parse_timestamps(item)
        item_xml = item_to_xml(item)
        q.enqueue('tasks.process_episode_item', item_xml)
    else:
        print(f"Episode {args.episode} not found." if args.episode else "No episodes found.")