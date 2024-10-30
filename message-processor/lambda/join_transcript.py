import json
import boto3
import hashlib
from lib.files import S3URI
import os

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['DYNO_TABLE'])
    
    transcript_parts = []    
    fragments = sorted(event['data']['files']['fragments'], key=lambda x: x['index'])
    
    for fragment in fragments:
        transcript_path = fragment['transcript']
        uri = S3URI(transcript_path)
        response = s3.get_object(Bucket=uri.bucket, Key=uri.key)
        transcript_content = response['Body'].read().decode('utf-8')        
        transcript_parts.append(transcript_content)
    
    full_transcript = " ".join(transcript_parts)
    channel_id = event['data']['channel_id']    
    content_id = event['data']['guid']
    
    key = {'Channel ID': channel_id, 'Content ID': content_id}

    table.update_item(
        Key=key,
        UpdateExpression='SET transcript = :transcript',
        ExpressionAttributeValues={
            ':transcript': full_transcript
        }
    )

    # Add the full transcript to the event
    event['data']['storage'] = key
    event['metadata']['steps'].append('TranscriptStored')
    
    return event