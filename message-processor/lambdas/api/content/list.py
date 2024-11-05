import json
import boto3
import os
from botocore.exceptions import ClientError
import logging
import urllib.parse
import lambdas.api.helpers.response as response

logger = logging.getLogger()
logger.setLevel(logging.ERROR)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['CONTENT_TABLE'])

def set_metadata_attributes(content_items):
    # "Metadata": {
    #     "duration": "10:27",
    #     "channel_title": "The Game w/ Alex Hormozi",
    #     "image": "https://artwork.captivate.fm/d2127b46-fbd8-4758-8234-29f2f7d803e0/y25Z330dpeR-fNTz7NWUOlog.jpg",
    #     "rss_url": "https://feeds.captivate.fm/the-game-alex-hormozi/",
    #     "length": "15047867",
    #     "guid": "28d03c0270f0db1f7002b2a592f51528",
    #     "description": "<p>Welcome to The Game w/Alex Hormozi, hosted by entrepreneur, founder, investor, author, public speaker, and content creator Alex Hormozi. On this podcast you’ll hear how to get more customers, make more profit per customer, how to keep them longer, and the many failures and lessons Alex has learned and will learn on his path from $100M to $1B in net worth.</p><p>Wanna scale your business? <a href=\"https://www.acquisition.com/poda\" rel=\"noopener noreferrer\" target=\"_blank\">Click here.</a></p><p><strong>Follow Alex Hormozi’s Socials:</strong></p><p><a href=\"https://www.linkedin.com/in/alexhormozi/\" rel=\"noopener noreferrer\" target=\"_blank\">LinkedIn&nbsp;</a> | <a href=\"https://www.instagram.com/hormozi/?hl=en\" rel=\"noopener noreferrer\" target=\"_blank\">Instagram</a> | <a href=\"https://www.facebook.com/alex.hormozi\" rel=\"noopener noreferrer\" target=\"_blank\">Facebook</a> | <a href=\"https://www.youtube.com/c/AlexHormozi\" rel=\"noopener noreferrer\" target=\"_blank\">YouTube&nbsp;</a> | <a href=\"https://twitter.com/AlexHormozi?s=20&amp;t=J9vPh75tO3ow9xExYLsBDQ\" rel=\"noopener noreferrer\" target=\"_blank\">Twitter</a> | <a href=\"https://www.acquisition.com/\" rel=\"noopener noreferrer\" target=\"_blank\">Acquisition&nbsp;</a></p>",
    #     "title": "2 Proven Scaling Paths for Service Businesses | Ep 787",
    #     "type": "audio/mpeg",
    #     "pubDate": "Mon, 04 Nov 2024 05:15:00 -0500",
    #     "channel_id": "7e92c78087de800e65eeac7845641e6a",
    #     "url": "https://podcasts.captivate.fm/media/abc3358e-ca21-456a-ba52-5d82aca0cb1b/C9220b.mp3"
    # }
    for item in content_items:
        metadata = item.pop('Metadata', {})
        item['channel_title'] = metadata.get('channel_title', 'Unknown')
        item['content_title'] = metadata.get('title', 'Unknown')
        item['content_image'] = metadata.get('image', None)
        item['content_pub_date'] = metadata.get('pubDate', None)

def get_user_content_items(user_id):
    user_content_table = dynamodb.Table(os.environ['USER_CONTENT_TABLE'])

    return user_content_table.query(
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
        ).get('Items', [])

def get_content_items(user_content_items):
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
        request_items = response.get('UnprocessedKeys', {})

    return content_items

def handler(event, context):
    user_id = event['pathParameters']['userID']
    user_id = urllib.parse.unquote(user_id)

    try:
        user_content_items = get_user_content_items(user_id)
        
        if not user_content_items:
            return response.success_response({'items': []})
        
        content_items = get_content_items(user_content_items    )
        set_metadata_attributes(content_items)     
    except ClientError as e:
        logger.error(e.response['Error']['Message'])
        return response.error_response('Error retrieving items from Datastore')
    
    return response.success_response({'items': content_items})