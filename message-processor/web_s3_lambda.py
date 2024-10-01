import json
import boto3
import requests
from urllib.parse import urlparse
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')
S3_BUCKET_NAME = os.environ['S3_BUCKET_NAME']

def lambda_handler(event, context):
    item_dict = event['data']
    media_url = item_dict.get('url')

    logger.info("Received event: " + json.dumps(event))

    if not media_url:
        logger.error("Media URL not found in the item.")
        return {
            'statusCode': 400,
            'body': json.dumps('Media URL not found in the item.')
        }

    file_extension = os.path.splitext(urlparse(media_url).path)[1]
    s3_key = f"media/{item_dict['guid']}{file_extension}"

    try:
        response = requests.get(media_url, stream=True)
        response.raise_for_status()

        # Upload the file to S3
        s3_client.upload_fileobj(response.raw, S3_BUCKET_NAME, s3_key)

        # Update item_dict with S3 location
        item_dict['files'] = {'full_length': f"s3://{S3_BUCKET_NAME}/{s3_key}"}

        # Update the event with the modified item_dict
        event['data'] = item_dict

        # Add a step to the metadata
        event['metadata']['steps'].append('MediaDownloadedToS3')

        logger.info(f"Media downloaded and uploaded to S3 successfully: s3://{S3_BUCKET_NAME}/{s3_key}")
        
        logger.info("Updated event: " + json.dumps(event))

        return event

    except requests.RequestException as e:
        logger.error(f"Failed to download media. Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Failed to download media. Error: {str(e)}")
        }
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"An error occurred: {str(e)}")
        }
