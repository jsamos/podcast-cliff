import json
from lib.files import S3URI

def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps('Hello World')
    }
