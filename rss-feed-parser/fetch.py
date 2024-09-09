from lib.rss import fetch_podcast_rss, fetch_episode_item
import argparse
import json
from redis import Redis
from rq import Queue
import xmltodict

redis_conn = Redis(host='redis', port=6379)
q = Queue('rss_queue', connection=redis_conn)


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
        print(f"Episode: '{dic['title']}' found.")
        q.enqueue('tasks.process_episode_item', json_output)
    else:
        print(f"Episode {args.title} not found." if args.title else "No episodes found.")
