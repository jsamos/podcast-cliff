import os
from multiprocessing import Process
from rq import Worker, Queue, Connection
from redis import Redis

listen = ['podcast_queue']
redis_conn = Redis(host='redis', port=6379)

def start_worker():
    with Connection(redis_conn):
        worker = Worker(map(Queue, listen))
        worker.work()

if __name__ == '__main__':
    num_workers = 2  # Number of workers to start
    processes = []

    for _ in range(num_workers):
        p = Process(target=start_worker)
        p.start()
        processes.append(p)

    for p in processes:
        p.join()