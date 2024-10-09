import json
import logging
import boto3
import tempfile
import os
from lib.transcription import transcribe_audio
from lib.files import S3URI

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')

def download_from_s3(s3_uri):
    uri = S3URI(s3_uri)
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
        temp_path = temp_file.name
        s3_client.download_file(uri.bucket, uri.key, temp_path)
    
    return temp_path

def transcribe_fragment(event):
    s3_uri = event['path']
    temp_audio_path = download_from_s3(s3_uri)
    
    try:
        transcript = transcribe_audio(temp_audio_path)
    finally:
        os.unlink(temp_audio_path)
    
    return transcript

def put_transcript_in_s3(transcript, s3_uri):
    s3_uri = S3URI(s3_uri)
    s3_client.put_object(Bucket=s3_uri.bucket, Key=s3_uri.key, Body=transcript)

def lambda_handler(event, context):
    try:
        logger.info(f"Received event: {event}")
        transcript = transcribe_fragment(event)
        transcript_path = f"{event['path']}.txt"
        put_transcript_in_s3(transcript, transcript_path)
        
        return transcript_path
    except Exception as e:
        logger.error(f"Error processing fragment: {str(e)}")
        raise e

# Example event:
# {
#     "index": 1,
#     "start": 0,
#     "end": 60,
#     "path": "s3://jsamos-podcast-cliff/temp/1243243214/0_60.wav"
# }

