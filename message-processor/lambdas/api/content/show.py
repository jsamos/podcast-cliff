import boto3
import os
import logging
import urllib.parse
from botocore.exceptions import ClientError
import lambdas.api.helpers.response as response_json

logger = logging.getLogger()
logger.setLevel(logging.ERROR)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['CONTENT_TABLE'])

def handler(event, context):
    channel_id = event['pathParameters']['channelID']
    content_id = event['pathParameters']['contentID']
    channel_id = urllib.parse.unquote(channel_id)
    content_id = urllib.parse.unquote(content_id)

    try:
        response = table.get_item(
            Key={
                'Channel ID': channel_id,
                'Content ID': content_id
            }
        )
        
        # Check if item was found
        if 'Item' not in response:
            json_response = response_json.not_found()
        else:
            item = response['Item']
            json_response = response_json.success_response({'item': item})
        
    except ClientError as e:
        logger.error(e.response['Error']['Message'])
        json_response = response_json.error_response('Error retrieving item from DynamoDB')
    
    # Return the response
    return json_response