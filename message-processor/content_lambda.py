import json
import boto3
import os
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger()
logger.setLevel(logging.ERROR)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNO_TABLE'])


def lambda_handler(event, context):
    # Extract path parameters
    channel_id = event['pathParameters']['channelID']
    content_id = event['pathParameters']['contentID']
    
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
