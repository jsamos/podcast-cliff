import json
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # Log the entire event for debugging
    logger.info("Received event: " + json.dumps(event))

    # Extract and log the body
    try:
        body = json.loads(event['body'])
        logger.info("Request body: " + json.dumps(body))
    except KeyError:
        logger.warning("No 'body' found in the event")
    except json.JSONDecodeError:
        logger.error("Failed to parse body as JSON")

    # Return a simple response
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Request received and logged'})
    }