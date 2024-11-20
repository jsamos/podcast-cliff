import os
import boto3
import lambdas.api.helpers.response as response

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['USER_CONTENT_TABLE'])

def handler(event, context):
    try:
        user_id = event['pathParameters']['userID']
        content_id = event['pathParameters']['contentID']
        
        table.delete_item(
            Key={
                'User ID': user_id,
                'Content ID': content_id
            }
        )
        
        return response.no_content_response()        
    except Exception as e:
        return response.error_response(f'Error deleting content: {str(e)}')
