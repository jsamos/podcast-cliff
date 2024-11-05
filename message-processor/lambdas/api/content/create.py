import uuid
import boto3
import json
import lambdas.api.helpers.response as response_json

stepfunctions = boto3.client('stepfunctions')

def handler(event, context):
    execution_id = str(uuid.uuid4())
    request_body = json.loads(event['body'])
    source_user_id = request_body.pop("user_id", None)

    message = {
        "data": request_body,
        "metadata": {
            "execution_id": execution_id,
            "source_user_id": source_user_id,
            "steps": ['APIRequestReceived']
        }
    }
    
    try:
        stepfunctions.start_execution(
            stateMachineArn='arn:aws:states:us-west-2:305578904386:stateMachine:MyStateMachine-0irnmroeq',
            input=json.dumps(message)
        )
        
        response_body = {
            'message': 'Process started successfully',
            'execution_id': execution_id,
            'status_url': f"/test/status/{execution_id}"
        }

        return response_json.success_response(response_body, 202)
    except Exception as e:
        return response_json.error_response('Failed to start process')
