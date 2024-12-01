import logging
import json
import hashlib
import lib.storage as storage
import lib.rss as rss

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    json_string = json.dumps(event)
    logger.info("Received Lambda Event: " + json_string)
    url = event['data']['rss_url']
    title = event['data']['title']
    episode_guid = event['data']['episode_guid']
    logger.info(f"Fetching episode from {url} guid: {episode_guid} and title: {title}")
    soup = rss.fetch_podcast_rss(url)
    item = rss.fetch_episode_item(soup, episode_guid)
    
    if item:
        event['data'] = {**event['data'], **rss.item_to_dict(item)} 
        event['data']['channel_id'] = hashlib.md5(event['data']['rss_url'].encode('utf-8')).hexdigest()
        event['data']['channel_title'] = rss.get_channel_title(soup)

        if not event['data']['image']:
            event['data']['image'] = rss.get_channel_image(soup)

        logger.info("Found episode: " + json.dumps(event))
        content_key = storage.get_content_key(event['data'])
        storage.store_content(content_key, event['data'], event['metadata'].get('source_user_id'))

        event['metadata']['storage'] = content_key
        event['metadata']['steps'].append('RSSFeedProcessed')
        return event
    else:
       logger.info("No episode found")
       return {"error": "No episode found"}
