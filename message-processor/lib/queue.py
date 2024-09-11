from rq import Queue
from lib.redis import redis_conn
q = Queue('podcast_queue', connection=redis_conn)