import json
import boto3
import requests
from urllib.parse import urlparse
import os
import logging
from lib.files import ensure_temp_prefix

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')
S3_BUCKET_NAME = os.environ['S3_BUCKET_NAME']

def get_s3_key(data):
    media_url = data.get('url')
    parsed_url = urlparse(media_url)
    file_name = os.path.basename(parsed_url.path)
    logger.info(f"File name: {file_name}")
    temp_prefix = ensure_temp_prefix(data)
    logger.info(f"Temp prefix: {temp_prefix}")
    s3_key = f"{temp_prefix}/{file_name}"
    logger.info(f"S3 key: {s3_key}")
    return s3_key

def lambda_handler(event, context):
    data = event['data']
    logger.info("Received event: " + json.dumps(event))
    media_url = data.get('url')
    response = requests.get(media_url, stream=True)
    response.raise_for_status()
    s3_key = get_s3_key(data)
    s3_client.upload_fileobj(response.raw, S3_BUCKET_NAME, s3_key)
    s3_uri = f"s3://{S3_BUCKET_NAME}/{s3_key}"
    data['files'] = {'full_length': s3_uri}
    event['data'] = data
    event['metadata']['steps'].append('MediaDownloadedToS3')
    logger.info(f"Media downloaded and uploaded to S3 successfully: {s3_uri}")
    logger.info("Updated event: " + json.dumps(event))
    return event

