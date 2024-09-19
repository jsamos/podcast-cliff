import logging
import json
from lib.rss import fetch_podcast_rss, fetch_episode_item, item_to_dict

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    json_string = json.dumps(event)
    logger.info("Received Lambda Event: " + json_string)

    url = dic['rss_url']
    title = dic['title']
    logger.info(f"Fetching episode from {url} and title: {title}")
    soup = fetch_podcast_rss(url)
    item = fetch_episode_item(soup, title)
    
    if item:
        dic = {**dic, **item_to_dict(item)} 
        logger.info("Found episode: " + json.dumps(dic))
        return dic
    else:
       logger.info("No episode found")
       return None
