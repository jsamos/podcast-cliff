import logging
import base64
from flask import Flask, request, jsonify
from redis import Redis
from rq import Queue
import os
from functools import wraps

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Redis and RQ setup
redis_conn = Redis(host=os.environ.get('REDIS_HOST'), port=os.environ.get('REDIS_PORT'))
q = Queue('podcast_queue', connection=redis_conn)

# Basic Auth setup
def check_auth(token):
    return token == os.environ.get('API_TOKEN')

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
            token = decoded_credentials.split(':')[0]  # We're using the username part as the token
        except:
            logger.warning("Failed to decode credentials")
            return authenticate()
        
        if not check_auth(token):
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
    job = q.enqueue('rss.feed_item_requested', data['rss_url'], data['title'])
    logger.info(f"Job enqueued with ID: {job.id}")
    return jsonify({"job_id": job.id}), 202

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('API_PORT'), debug=True)