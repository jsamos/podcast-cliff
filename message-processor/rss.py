from lib.rss import fetch_podcast_rss, fetch_episode_item, item_to_dict
from redis import Redis
from rq import Queue
import json
from lib.queue import q
from lib.events import Events

def feed_item_requested(json_string):
    dic = json.loads(json_string)
    url = dic['rss_url']
    title = dic['title']
    print(f"Fetching episode from {url} and title: {title}")

    soup = fetch_podcast_rss(url)
    item = fetch_episode_item(soup, title)
    
    if item:
        dic = {**dic, **item_to_dict(item)} 
        json_output = json.dumps(dic)
        print(f"Episode: '{dic['title']}' found.")
        Events.fire('rss_feed_item_found', dic)
    else:
        print(f"Episode {args.title} not found." if args.title else "No episodes found.")