import redis
import json
from datetime import datetime
import os

# Initialize Redis connection
redis_client = redis.Redis(host=os.environ.get('REDIS_HOST'), port=os.environ.get('REDIS_PORT'))

def create_job_status(job_id):
    job_key = f"job:{job_id}"
    timestamp = datetime.utcnow().isoformat()
    
    # Create a hash for the job
    redis_client.hset(job_key, mapping={
        "status": "queued",
        "progress": "0%",
        "created_at": timestamp,
        "updated_at": timestamp
    })
    
    # Initialize the updates list
    #redis_client.rpush(f"{job_key}:updates", "Job queued")

def get_job_status(job_id):
    job_key = f"job:{job_id}"
    
    # Get the job hash
    job_data = redis_client.hgetall(job_key)
    
    if not job_data:
        return None
    
    # Convert byte strings to regular strings
    job_data = {k.decode(): v.decode() for k, v in job_data.items()}
    
    return job_data