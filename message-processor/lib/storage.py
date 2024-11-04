import boto3
import os
from lib.files import S3URI

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# S3 functions
def fetch_s3_object(s3_uri):
    uri = S3URI(s3_uri)
    response = s3.get_object(Bucket=uri.bucket, Key=uri.key)
    return response['Body'].read().decode('utf-8')

def fetch_transcript_fragment(s3_uri):
    return fetch_s3_object(s3_uri)

def get_llm_system_message():
    uri = S3URI(os.environ['CHAT_SYSTEM_MESSAGE_S3_URI'])
    response = s3.get_object(Bucket=uri.bucket, Key=uri.key)
    return response['Body'].read().decode('utf-8')


# DynamoDB functions
def get_content_key(data):
    return {'Channel ID': data['channel_id'], 'Content ID': data['guid']}

def put_transcript(key, transcript):
    main_table = dynamodb.Table(os.environ['CONTENT_TABLE'])
    
    main_table.update_item(
        Key=key,
        UpdateExpression='SET transcript = :transcript',
        ExpressionAttributeValues={':transcript': transcript}
    )

    return True

def get_transcript(key):
    table = dynamodb.Table(os.environ['CONTENT_TABLE'])
    response = table.get_item(Key=key)
    return response.get('Item', {}).get('transcript', '')

def put_ebook(key, ebook_content):
    table = dynamodb.Table(os.environ['CONTENT_TABLE'])
    
    table.update_item(
        Key=key,
        UpdateExpression='SET ebook = :ebook',
        ExpressionAttributeValues={':ebook': ebook_content}
    )

    return True

def put_user_content(user_id, content_key):
    user_table = dynamodb.Table(os.environ['USER_CONTENT_TABLE'])
    user_table.put_item(Item={
        'User ID': user_id,
        **content_key
    })

def store_content(key, metadata={}, source_user_id=None):
    content_table = dynamodb.Table(os.environ['CONTENT_TABLE'])
    
    content_table.put_item(Item={
        **key, 
        'Metadata': metadata
    })

    if source_user_id:
        put_user_content(source_user_id, key)