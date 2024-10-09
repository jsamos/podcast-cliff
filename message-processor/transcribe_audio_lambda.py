import json
import logging
import boto3
import tempfile
import os
from lib.transcription import transcribe_audio

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')

def download_from_s3(s3_uri):
    bucket_name = s3_uri.split('//')[1].split('/')[0]
    s3_key = '/'.join(s3_uri.split('//')[1].split('/')[1:])
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
        temp_path = temp_file.name
        s3_client.download_file(bucket_name, s3_key, temp_path)
    
    return temp_path

def transcribe_fragment(event):
    s3_uri = event['path']
    temp_audio_path = download_from_s3(s3_uri)
    
    try:
        transcript = transcribe_audio(temp_audio_path)
    finally:
        os.unlink(temp_audio_path)
    
    return transcript

def lambda_handler(event, context):
    try:
        logger.info(f"Received event: {event}")
        
        transcript = transcribe_fragment(event)
        
        return transcript
    except Exception as e:
        logger.error(f"Error processing fragment: {str(e)}")
        raise e

# Example event:
# {
#     "index": 1,
#     "start": 0,
#     "end": 60,
#     "path": "s3://jsamos-podcast-cliff/fragments/0_60.wav"
# }

