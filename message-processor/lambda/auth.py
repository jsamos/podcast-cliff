import json
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Hardcoded API key for simplicity (you can store it in an environment variable or AWS Secrets Manager)
VALID_API_KEY = os.environ['API_KEY']

def lambda_handler(event, context):
    # Log the incoming event for debugging (if needed)
    print("Received event:", json.dumps(event))

    # Extract the authorization header
    identity_source = event.get('identitySource', [])
    if not identity_source or not identity_source[0].startswith('Bearer '):
        return generate_policy("Deny", event['routeArn'], "Unauthorized: No valid API Key provided")

    # Extract the Bearer token (the part after 'Bearer ')
    api_key = identity_source[0].split(' ')[1]

    # Validate the API key
    if api_key == VALID_API_KEY:
        return generate_policy("Allow", event['routeArn'], "API Key valid")
    else:
        return generate_policy("Deny", event['routeArn'], "Unauthorized: Invalid API Key")


def generate_policy(effect, resource, reason):
    policy = {
        'principalId': 'user',  # Use a static user or dynamic information based on your logic
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Action': 'execute-api:Invoke',
                    'Effect': effect,
                    'Resource': resource
                }
            ]
        },
        'context': {
            'message': reason
        }
    }
    return policy