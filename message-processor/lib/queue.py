from redis import Redis
from rq import Queue

redis_conn = Redis(host='redis', port=6379)
q = Queue('podcast_queue', connection=redis_conn)