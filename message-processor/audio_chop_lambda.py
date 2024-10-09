import json
import os
import logging
from lib import audio
from config import AUDIO_FRAGMENT_LENGTH

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        logger.info(f"Received event: {event}")
        # Extract the S3 URI from the event
        data = event.get('data', {})
        files = data.get('files', {})
        s3_uri = files.get('full_length')

        if not s3_uri:
            raise ValueError("No 'full_length' S3 URI provided in the event data")

        logger.info(f"Processing audio file: {s3_uri}")

        # Initialize S3AudioFileManager
        s3_manager = audio.S3AudioFileManager(s3_uri)

        # Create audio fragments
        fragments = audio.create_audio_fragments(s3_manager, AUDIO_FRAGMENT_LENGTH)

        logger.info(f"Created {len(fragments)} audio fragments")
        data['files']['fragments'] = fragments
        event['metadata']['steps'].append('AudioChopped')
        return event

    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error processing audio',
                'error': str(e)
            })
        }
