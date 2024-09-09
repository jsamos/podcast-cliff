import argparse
from redis import Redis
from rq import Queue

redis_conn = Redis(host='redis', port=6379)
q = Queue('podcast_queue', connection=redis_conn)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and enqueue episode item from an RSS feed")
    parser.add_argument('rss_url', type=str, help='URL of the RSS feed')
    parser.add_argument('--title', type=str, help='Episode title to fetch', default=None)
    args = parser.parse_args()
    q.enqueue('rss.feed_item_requested', args.rss_url, args.title)
