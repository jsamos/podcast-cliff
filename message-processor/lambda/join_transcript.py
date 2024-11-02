import boto3
from lib.files import S3URI
import os

def join_fragments(fragments):
    s3 = boto3.client('s3')
    transcript_parts = []    
    for fragment in fragments:
        uri = S3URI(fragment['transcript'])
        response = s3.get_object(Bucket=uri.bucket, Key=uri.key)
        transcript_content = response['Body'].read().decode('utf-8')        
        transcript_parts.append(transcript_content)
    return " ".join(transcript_parts)

def store_transcript(channel_id, content_id, transcript, source_user_id=None):
    dynamodb = boto3.resource('dynamodb')
    main_table = dynamodb.Table(os.environ['CONTENT_TABLE'])
    user_table = dynamodb.Table(os.environ['USER_CONTENT_TABLE'])
    
    # Store main transcript
    key = {'Channel ID': channel_id, 'Content ID': content_id}
    main_table.update_item(
        Key=key,
        UpdateExpression='SET transcript = :transcript',
        ExpressionAttributeValues={':transcript': transcript}
    )

    # Store user mapping if source_user_id is provided
    if source_user_id:
        user_table.put_item(Item={
            'User ID': source_user_id,
            'Content ID': content_id,
            'Channel ID': channel_id
        })

    return key

def lambda_handler(event, context):
    fragments = sorted(event['data']['files']['fragments'], key=lambda x: x['index'])
    transcript = join_fragments(fragments)
    channel_id = event['data']['channel_id']    
    content_id = event['data']['guid']
    source_user_id = event['metadata'].get('source_user_id')
    event['data']['storage'] = store_transcript(channel_id, content_id, transcript, source_user_id)
    event['metadata']['steps'].append('TranscriptStored')
    return event