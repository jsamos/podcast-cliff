import json
import boto3
import os

s3_client = boto3.client('s3')
S3_BUCKET_NAME = os.environ['S3_BUCKET_NAME']

def lambda_handler(event, context):
    try:
        # Get the data from the event
        data = event.get('data', {})
        files = data.get('files', {})

        # List of keys to check for deletion
        keys_to_delete = ['full_length']  # Start with 'full_length', add more as needed

        deleted_files = []

        for key in keys_to_delete:
            if key in files:
                file_paths = files[key]
                if isinstance(file_paths, str):
                    file_paths = [file_paths]
                elif not isinstance(file_paths, list):
                    continue

                for file_path in file_paths:
                    # Extract the S3 key from the S3 URI
                    s3_key = file_path.split(f"s3://{S3_BUCKET_NAME}/", 1)[-1]
                    
                    # Delete the file
                    s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
                    deleted_files.append(s3_key)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Files deleted successfully',
                'deleted_files': deleted_files
            })
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error deleting files',
                'error': str(e)
            })
        }
