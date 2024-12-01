import requests
from bs4 import BeautifulSoup
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

def find_item_by_guid(soup, episode_guid):
    for item in soup.find_all('item'):
        guid_tag = item.find('guid')
        if guid_tag and guid_tag.text == episode_guid:
            return item
    return None

def fetch_episode_item(soup, episode_guid=None):
    if not episode_guid:
        return soup.find('item')
    return find_item_by_guid(soup, episode_guid)

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

