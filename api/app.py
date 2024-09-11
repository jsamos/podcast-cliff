import logging
import base64
from flask import Flask, request, jsonify
from redis import Redis
from rq import Queue
import os
from functools import wraps
import uuid
import json
from lib.status import get_job_status, create_job_status

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG') == '1'

# Redis and RQ setup
redis_conn = Redis(host=os.environ.get('REDIS_HOST'), port=os.environ.get('REDIS_PORT'))
q = Queue('podcast_queue', connection=redis_conn)

# Basic Auth setup
def check_auth(username, password):
    return username == os.environ.get('API_USERNAME') and password == os.environ.get('API_PASSWORD')

def authenticate():
    return jsonify({"error": "Authentication required"}), 401, {'WWW-Authenticate': 'Basic realm="API"'}

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Basic '):
            logger.warning("Missing or invalid Authorization header")
            return authenticate()
        
        encoded_credentials = auth_header.split(' ')[1]
        try:
            decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
            username, password = decoded_credentials.split(':')
        except:
            logger.warning("Failed to decode credentials")
            return authenticate()
        
        if not check_auth(username, password):
            logger.warning("Invalid token provided")
            return authenticate()
        
        return f(*args, **kwargs)
    return decorated

@app.route('/', methods=['GET'])
def ping():
    return jsonify({"message": "bro!"}), 200

@app.route('/transcribe/rss', methods=['POST'])
@requires_auth
def transcribe_rss():
    data = request.json
    job_id = str(uuid.uuid4())
    
    dic = {
        'job_id': job_id,
        'rss_url': data['rss_url'],
        'title': data['title']
    }

    json_output = json.dumps(dic)
    job = q.enqueue('rss.feed_item_requested', json_output)
    logger.info(f"Job enqueued with ID: {job_id}")
    create_job_status(job_id)
    return jsonify({"job_id": job_id}), 202

@app.route('/job/<job_id>', methods=['GET'])
@requires_auth
def check_job_status(job_id):
    job_status = get_job_status(job_id)
    if job_status is None:
        return jsonify({"error": "Job not found"}), 404
    
    return jsonify(job_status), 200

if __name__ == '__main__':
    app.run()