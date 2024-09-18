import json
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # Log the entire event for debugging
    logger.info("Received event: " + json.dumps(event))

    # Modify the event directly
    event['lambda1'] = 'Hello from Lambda 1'

    # Log the modified event
    logger.info("Modified event: " + json.dumps(event))

    # Return the modified event
    return event
