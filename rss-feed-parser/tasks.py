from lib.rss import fetch_podcast_rss, fetch_episode_item, item_to_dict
from redis import Redis
from rq import Queue
import json

redis_conn = Redis(host='redis', port=6379)
q = Queue('rss_queue', connection=redis_conn)
podcast_queue = Queue('podcast_queue', connection=redis_conn)

def rss_feed_item_requested(url, title=None):
    print(f"Fetching episode from {url} and title: {title}")

    soup = fetch_podcast_rss(url)
    item = fetch_episode_item(soup, title)
    
    if item:
        dic = item_to_dict(item)
        json_output = json.dumps(dic)
        print(f"Episode: '{dic['title']}' found.")
        podcast_queue.enqueue('web.media_download_requested', json_output)
    else:
        print(f"Episode {args.title} not found." if args.title else "No episodes found.")