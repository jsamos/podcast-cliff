import argparse
import os
from bs4 import BeautifulSoup
from redis import Redis
from rq import Queue
import json

# Establish Redis connection and queue
redis_conn = Redis(host='redis', port=6379)
q = Queue('podcast_queue', connection=redis_conn)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create XML for an episode")
    parser.add_argument('filepath', type=str, help='Path to the audio file')
    args = parser.parse_args()
    filepath = args.filepath
    episode_title = os.path.basename(filepath).replace('.mp3', '').replace('-', ' ')

    dict = {
        'title': episode_title,
        'files': {
            'full_length': filepath
        },
        'description': "Content description"
    }

json_output = json.dumps(dic)
    q.enqueue('audio.new_file_present', json_string)