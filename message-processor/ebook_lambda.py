import json
import os
import boto3
from openai import OpenAI
from botocore.exceptions import ClientError
import logging
from lib.files import S3URI

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
openai_client = OpenAI()

def get_system_message_from_s3():
    uri = S3URI(os.environ['CHAT_SYSTEM_MESSAGE_S3_URI'])
    response = s3.get_object(Bucket=uri.bucket, Key=uri.key)
    return response['Body'].read().decode('utf-8')

def get_transcript_from_dynamodb(channel_id, content_id):
    table = dynamodb.Table(os.environ['DYNO_TABLE'])
    try:
        response = table.get_item(
            Key={
                'Channel ID': channel_id,
                'Content ID': content_id
            }
        )
        if 'Item' in response:
            return response['Item'].get('transcript', '')
        else:
            logger.error(f"Item not found for Channel ID: {channel_id}, Content ID: {content_id}")
            return None
    except ClientError as e:
        logger.error(f"Error retrieving item from DynamoDB: {e.response['Error']['Message']}")
        return None

def lambda_handler(event, context):
    try:
        storage = event['data']['storage']
        channel_id = storage['Channel ID']
        content_id = storage['Content ID']
        
        # Get the transcript from DynamoDB
        transcript = get_transcript_from_dynamodb(channel_id, content_id)
        if transcript is None:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Transcript not found'})
            }
        
        system_message = get_system_message_from_s3()
        model = os.environ['OPENAI_MODEL']
        user_message = f"I have a transcript I need you to convert to an Ebook: {transcript}"
        # Make the request to OpenAI
        completion = openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
        )

        # Extract the assistant's response
        ebook_content = completion.choices[0].message.content
        logger.info(f"Ebook generated successfully: {ebook_content}")

        # Store the ebook in DynamoDB
        table = dynamodb.Table(os.environ['DYNO_TABLE'])
        table.update_item(
            Key={'Channel ID': channel_id, 'Content ID': content_id},
            UpdateExpression='SET ebook = :ebook',
            ExpressionAttributeValues={':ebook': ebook_content}
        )

        logger.info(f"Ebook stored in DynamoDB for Channel ID: {channel_id}, Content ID: {content_id}")

        # Update the event
        
        event['metadata']['steps'].append('EbookGenerated')
        logger.info(f"Event after update: {event}")

        return event
        
    except KeyError as e:
        logger.error(f"Missing required key in event data: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f"Missing required key: {str(e)}"}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
