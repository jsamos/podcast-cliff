from redis import Redis
from rq import Queue
import os

redis_conn = Redis(host=os.environ.get('REDIS_HOST'), port=os.environ.get('REDIS_PORT'))
q = Queue('podcast_queue', connection=redis_conn)