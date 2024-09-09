import os
from rq import Worker, Queue, Connection
from redis import Redis

listen = ['podcast_queue']
redis_conn = Redis(host='redis', port=6379)

if __name__ == '__main__':
    with Connection(redis_conn):
        worker = Worker(map(Queue, listen))
        worker.work()