import requests
from bs4 import BeautifulSoup
import argparse
import re
from redis import Redis
from rq import Queue
import lxml.etree as ET
from difflib import SequenceMatcher
import xmltodict
import json

redis_conn = Redis(host='redis', port=6379)
q = Queue('rss_queue', connection=redis_conn)


def similarity(a, b):
    """Calculate the similarity between two strings."""
    return SequenceMatcher(None, a, b).ratio()

def fetch_podcast_rss(rss_url):
    response = requests.get(rss_url)
    response.raise_for_status()
    return BeautifulSoup(response.content, 'xml')

def fetch_episode_item(soup, search_query=None, similarity_threshold=0.5):
    items = soup.find_all('item')
    best_match = None
    highest_similarity = 0

    for item in items:
        title = item.find('title').text.lower()
        search_query_lower = search_query.lower()

        # Calculate similarity
        current_similarity = similarity(title, search_query_lower)

        # Update best match if current item is more similar than previous best
        if current_similarity > highest_similarity and current_similarity >= similarity_threshold:
            best_match = item
            highest_similarity = current_similarity

    return best_match

def item_to_xml(item):
    # Extract the XML as a string with namespaces properly defined
    item_soup = BeautifulSoup(str(item), 'xml')
    return str(item_soup)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and enqueue episode item from an RSS feed")
    parser.add_argument('rss_url', type=str, help='URL of the RSS feed')
    parser.add_argument('--title', type=str, help='Episode title to fetch', default=None)
    args = parser.parse_args()
    soup = fetch_podcast_rss(args.rss_url)
    item = fetch_episode_item(soup, args.title)
    
    if item:
        dic = {
            'guid': item.find('guid').text,
            'title': item.find('title').text,
            'creator': item.find('creator').text,
            'description': item.find('description').text,
            'pubDate': item.find('pubDate').text,
            'url': item.find('enclosure').get('url'),
            'length': item.find('enclosure').get('length'),
            'duration': item.find('itunes:duration').text,
            'type': item.find('enclosure').get('type')
        }

        json_output = json.dumps(dic)
        q.enqueue('tasks.process_episode_item', json_output)
    else:
        print(f"Episode {args.title} not found." if args.title else "No episodes found.")
