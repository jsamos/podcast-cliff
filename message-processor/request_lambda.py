import uuid
import boto3
import os
import json

# Initialize AWS clients
stepfunctions = boto3.client('stepfunctions')

def lambda_handler(event, context):
    # Generate a unique ID for this execution
    execution_id = str(uuid.uuid4())

    body = json.loads(event['body'])

    message = {
        "data": body,
        "metadata": {
            "execution_id": execution_id,
            "steps": ['APIRequestReceived']
        }
    }
    
    try:
        # Start Step Function execution
        response = stepfunctions.start_execution(
            stateMachineArn='arn:aws:states:us-west-2:305578904386:stateMachine:MyStateMachine-0irnmroeq',
            input=json.dumps(message)
        )
        
        # Prepare response for API Gateway
        return {
            'statusCode': 202,  # Accepted
            'body': json.dumps({
                'message': 'Process started successfully',
                'execution_id': execution_id,
                'status_url': f"/test/status/{execution_id}"
            })
        }
    except Exception as e:
        print(f"Error starting Step Function: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to start process'})
        }
