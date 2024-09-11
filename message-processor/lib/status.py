
import json
from datetime import datetime
from lib.redis import redis_conn

def update_job_status(job_id, status, progress=None, details=None):
    job_key = f"job:{job_id}"
    timestamp = datetime.utcnow().isoformat()
    
    # Update the job hash
    update_data = {
        "status": status,
        "updated_at": timestamp
    }

    if progress:
        update_data["progress"] = progress
    
    if details:
        update_data["details"] = details
    
    redis_conn.hset(job_key, mapping=update_data)
    
    # Add a detailed update to the list
    # update_message = f"Status: {status}"
    # if progress:
    #     update_message += f", Progress: {progress}"
    # if details:
    #     update_message += f", Details: {details}"
    
    # redis_conn.rpush(f"{job_key}:updates", update_message)