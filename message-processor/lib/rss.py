import requests
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
import hashlib

def fetch_podcast_rss(rss_url):
    response = requests.get(rss_url)
    response.raise_for_status()
    return BeautifulSoup(response.content, 'xml')

def get_channel_image(soup):
    """Safely get channel image URL from RSS feed"""
    channel = soup.find('channel')
    if not channel:
        return None
    
    image = channel.find('image')
    if not image:
        return None
        
    url = image.find('url')
    return url.text if url else None

def similarity(a, b):
    """Calculate the similarity between two strings."""
    return SequenceMatcher(None, a, b).ratio()

def fetch_episode_item(soup, search_query=None, similarity_threshold=0.5):
    items = soup.find_all('item')
   
    if not search_query:
        return items[0]

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

def safe_find(item, tag, attribute=None):
    element = item.find(tag)
    if not element:
        return None
    return element.get(attribute) if attribute else element.text

def item_to_dict(item):
    return {
            'guid':  hashlib.md5(safe_find(item, 'guid').encode('utf-8')).hexdigest(),
            'title': safe_find(item, 'title'),
            'description': safe_find(item, 'description'),
            'pubDate': safe_find(item, 'pubDate'),
            'url': safe_find(item, 'enclosure', 'url'),
            'length': safe_find(item, 'enclosure', 'length'),
            'type': safe_find(item, 'enclosure', 'type'),
            'duration': safe_find(item, 'itunes:duration'),
            'image': safe_find(item, 'itunes:image', 'href')
    }

def get_channel_title(soup):
    return soup.find('channel').find('title').text

