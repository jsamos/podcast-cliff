import json
import boto3
import os
import traceback
import logging
import urllib.parse
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

def lambda_handler(event, context):
    execution_id = event['pathParameters']['executionID']    
    table_name = os.environ['DYNO_TABLE']
    table = dynamodb.Table(table_name)
    stage = event.get('requestContext', {}).get('stage', 'test')
    logger.info(f"Stage: {stage}")
    
    try:
        # Query the table by partition key (e.g., 'Task ID')
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
                    channel_id = event_data['data']['storage']['Channel ID']
                    content_id = event_data['data']['storage']['Content ID']
                    encoded_channel_id = urllib.parse.quote(channel_id)
                    encoded_content_id = urllib.parse.quote(content_id)
                    body['content'] = f"/content/{encoded_channel_id}/{encoded_content_id}"
                
                return {
                    'statusCode': 200,
                    'body': json.dumps(body)
                }
            else:
                return {
                    'statusCode': 404,
                    'body': json.dumps({'message': 'EventData not found'})
                }
        else:
            # If no item is found, return a 404 response
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'Item not found'})
            }
    
    except Exception as e:
        # Handle any errors that occurred during the query
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Internal Server Error',
                'error': str(e),
                'traceback': ''.join(traceback.format_tb(e.__traceback__))
            })
        }