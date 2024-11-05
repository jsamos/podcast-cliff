import json
import boto3
import os
import logging
import urllib.parse
import lambdas.api.helpers.response as response_json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize the DynamoDB resource
dynamodb = boto3.resource('dynamodb')

def calculate_progress(steps):
    progress_map = {
        "EbookGenerated": "100%",
        "TranscriptStored": "80%",
        "AudioChopped": "40%",
        "MediaDownloadedToS3": "15%",
        "RSSFeedProcessed": "10%",
        "APIRequestReceived": "5%"
    }
    
    for step in progress_map:
        if step in steps:
            return progress_map[step]
    
    return "0%"

def get_content_path(storage_data):
    channel_id = storage_data['Channel ID']
    content_id = storage_data['Content ID']
    encoded_channel_id = urllib.parse.quote(channel_id)
    encoded_content_id = urllib.parse.quote(content_id)
    return f"/content/{encoded_channel_id}/{encoded_content_id}"

def handler(event, context):
    execution_id = event['pathParameters']['executionID']    
    table_name = os.environ['DYNO_TABLE']
    table = dynamodb.Table(table_name)
    stage = event.get('requestContext', {}).get('stage', 'test')
    logger.info(f"Stage: {stage}")
    
    try:
        response = table.get_item(
            Key={
                'Task ID': execution_id
            }
        )
        
        # Check if the item was found
        if 'Item' in response:
            # Extract the EventData.S JSON string
            item = response['Item']
            event_data_str = item.get('EventData', '')
            
            if event_data_str:
                # Parse the JSON string into a dictionary
                event_data = json.loads(event_data_str)
                
                # Extract metadata.steps
                steps = event_data.get('metadata', {}).get('steps', [])
                body = {'steps': steps}

                # Calculate progress based on steps
                progress = calculate_progress(steps)
                body['progress'] = progress

                if 'storage' in event_data['data']:
                    body['content'] = get_content_path(event_data['data']['storage'])

                if 'storage' in event_data['metadata']:
                    body['content'] = get_content_path(event_data['metadata']['storage'])

                return response_json.success_response(body)
            else:
                return response_json.not_found()
        else:
            return response_json.not_found()
    
    except Exception as e:
        return response_json.error_response(str(e))