import json
import boto3
import os
import traceback
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize the DynamoDB resource
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    # Get the executionID from the API Gateway path parameters
    execution_id = event['pathParameters']['executionID']
    
    # Define your DynamoDB table DYNO_TABLE
    table_name = os.environ['DYNO_TABLE']
    
    # Initialize the DynamoDB table
    table = dynamodb.Table(table_name)
    
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
            logger.info(f"Item: {item}")
            event_data_str = item.get('EventData', '')
            logger.info(f"EventData: {event_data_str}")
            
            if event_data_str:
                # Parse the JSON string into a dictionary
                event_data = json.loads(event_data_str)
                
                # Extract metadata.steps
                steps = event_data.get('metadata', {}).get('steps', [])
                
                return {
                    'statusCode': 200,
                    'body': json.dumps({'steps': steps})
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