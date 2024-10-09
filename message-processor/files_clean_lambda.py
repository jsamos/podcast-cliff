import json
import boto3
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')
S3_BUCKET_NAME = os.environ['S3_BUCKET_NAME']

def lambda_handler(event, context):
    try:
        logger.info(f"Received event: {event}")
        deleted_files = []
        temp_prefix = event['data']['temp_prefix']

        paginator = s3_client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=S3_BUCKET_NAME, Prefix=temp_prefix):
            if 'Contents' in page:
                for obj in page['Contents']:
                    s3_key = obj['Key']
                    s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
                    logger.info(f"Deleted fragment file: {s3_key}")
                    deleted_files.append(s3_key)

        logger.info(f"Deleted files: {deleted_files}")
        event['metadata']['steps'].append('FilesCleaned')
        return event

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error deleting files',
                'error': str(e)
            })
        }
