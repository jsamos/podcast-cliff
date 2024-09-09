from flask import Flask, request, jsonify
from redis import Redis
from rq import Queue
import os
from functools import wraps

app = Flask(__name__)

# Redis and RQ setup
redis_conn = Redis(host=os.environ.get('REDIS_HOST'), port=os.environ.get('REDIS_PORT'))
q = Queue('podcast_queue', connection=redis_conn)

# Basic Auth setup
def check_auth(username, password):
    return username == os.environ.get('API_USERNAME') and password == os.environ.get('API_PASSWORD')

def authenticate():
    return jsonify({"error": "Authentication required"}), 401, {'WWW-Authenticate': 'Basic realm="Login Required"'}

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/', methods=['GET'])
def ping():
    return jsonify({"message": "bro!"}), 200

@app.route('/transcribe/rss', methods=['POST'])
@requires_auth
def publish_message():
    data = request.json
    return jsonify({"message": data}), 200

    if not data or 'message' not in data:
        return jsonify({"error": "Invalid request"}), 400
    
    job = q.enqueue('process_message', data['message'])
    return jsonify({"job_id": job.id}), 202

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)