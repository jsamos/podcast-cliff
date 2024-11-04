import logging
import json
from lib.rss import fetch_podcast_rss, fetch_episode_item, item_to_dict, get_channel_title
import hashlib
import lib.storage as storage

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    json_string = json.dumps(event)
    logger.info("Received Lambda Event: " + json_string)

    url = event['data']['rss_url']
    title = event['data']['title']
    logger.info(f"Fetching episode from {url} and title: {title}")
    soup = fetch_podcast_rss(url)
    item = fetch_episode_item(soup, title)
    
    if item:
        event['data'] = {**event['data'], **item_to_dict(item)} 
        event['data']['channel_id'] = hashlib.md5(event['data']['rss_url'].encode('utf-8')).hexdigest()
        event['data']['channel_title'] = get_channel_title(soup)
        logger.info("Found episode: " + json.dumps(event))
        content_key = storage.get_content_key(event['data'])
        storage.store_content(content_key, event['data'], event['metadata'].get('source_user_id'))

        event['metadata']['storage'] = content_key
        event['metadata']['steps'].append('RSSFeedProcessed')
        return event
    else:
       logger.info("No episode found")
       return {"error": "No episode found"}
