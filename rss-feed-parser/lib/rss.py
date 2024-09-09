import requests
from bs4 import BeautifulSoup
from difflib import SequenceMatcher

def fetch_podcast_rss(rss_url):
    response = requests.get(rss_url)
    response.raise_for_status()
    return BeautifulSoup(response.content, 'xml')

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

def item_to_dict(item):
    return {
            'guid': item.find('guid').text,
            'title': item.find('title').text,
            #'creator': item.find('creator').text,
            'description': item.find('description').text,
            'pubDate': item.find('pubDate').text,
            'url': item.find('enclosure').get('url'),
            'length': item.find('enclosure').get('length'),
            'duration': item.find('itunes:duration').text,
            'type': item.find('enclosure').get('type')
    }