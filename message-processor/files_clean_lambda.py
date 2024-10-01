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
        # Get the data from the event
        data = event.get('data', {})
        files = data.get('files', {})

        deleted_files = []

        # Delete full_length file
        if 'full_length' in files:
            full_length_path = files['full_length']
            s3_key = full_length_path.split(f"s3://{S3_BUCKET_NAME}/", 1)[-1]
            s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
            logger.info(f"Deleted full_length file: {s3_key}")
            deleted_files.append(s3_key)

        # Delete fragment files
        if 'fragments' in files:
            for fragment in files['fragments']:
                if 'path' in fragment:
                    fragment_path = fragment['path']
                    s3_key = fragment_path.split(f"s3://{S3_BUCKET_NAME}/", 1)[-1]
                    s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
                    logger.info(f"Deleted fragment file: {s3_key}")
                    deleted_files.append(s3_key)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Files deleted successfully',
                'deleted_files': deleted_files
            })
        }

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error deleting files',
                'error': str(e)
            })
        }
