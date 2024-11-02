import json
import boto3
import os
from botocore.exceptions import ClientError
import logging
import urllib.parse

logger = logging.getLogger()
logger.setLevel(logging.ERROR)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['CONTENT_TABLE'])


def show(event, context):
    # Extract path parameters
    channel_id = event['pathParameters']['channelID']
    content_id = event['pathParameters']['contentID']
    channel_id = urllib.parse.unquote(channel_id)
    content_id = urllib.parse.unquote(content_id)

    try:
        # Query DynamoDB
        response = table.get_item(
            Key={
                'Channel ID': channel_id,
                'Content ID': content_id
            }
        )
        
        # Check if item was found
        if 'Item' in response:
            item = response['Item']

            response_body = {
                'item': item
            }
            
            status_code = 200
        else:
            response_body = {
                'message': 'Item not found'
            }
            status_code = 404
        
    except ClientError as e:
        logger.error(e.response['Error']['Message'])
        response_body = {
            'message': 'Error retrieving item from DynamoDB'
        }
        status_code = 500
    
    # Return the response
    return {
        'statusCode': status_code,
        'body': json.dumps(response_body),
        'headers': {
            'Content-Type': 'application/json'
        }
    }

def list(event, context):
    # Extract user_id from path parameters
    user_id = event['pathParameters']['userID']
    user_id = urllib.parse.unquote(user_id)

    try:
        # Initialize the user content table
        user_content_table = dynamodb.Table(os.environ['USER_CONTENT_TABLE'])
        
        # Query USER_CONTENT_TABLE to get all content mappings for this user
        user_content_response = user_content_table.query(
            KeyConditionExpression='#uid = :uid',
            ExpressionAttributeNames={
                '#uid': 'User ID',
                '#cid': 'Channel ID',
                '#ctid': 'Content ID'
            },
            ProjectionExpression='#cid, #ctid',
            ExpressionAttributeValues={
                ':uid': user_id
            }
        )
        
        user_content_items = user_content_response.get('Items', [])
        
        # If no items found for user, return empty list
        if not user_content_items:
            return {
                'statusCode': 200,
                'body': json.dumps({'items': []}),
                'headers': {'Content-Type': 'application/json'}
            }

        # Prepare keys for batch get using both Channel ID and Content ID
        request_items = {
            os.environ['CONTENT_TABLE']: {
                'Keys': [
                    {
                        'Channel ID': item['Channel ID'],
                        'Content ID': item['Content ID']
                    }
                    for item in user_content_items
                ]
            }
        }
        
        # BatchGetItem can only process up to 100 items at a time
        content_items = []
        while request_items:
            response = dynamodb.batch_get_item(RequestItems=request_items)
            content_items.extend(response.get('Responses', {}).get(os.environ['CONTENT_TABLE'], []))
            
            # Handle any unprocessed items
            request_items = response.get('UnprocessedKeys', {})
        
        response_body = {
            'items': content_items
        }
        status_code = 200
        
    except ClientError as e:
        logger.error(e.response['Error']['Message'])
        response_body = {
            'message': 'Error retrieving items from Datastore'
        }
        status_code = 500
    
    return {
        'statusCode': status_code,
        'body': json.dumps(response_body),
        'headers': {'Content-Type': 'application/json'}
    }
