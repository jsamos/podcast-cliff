import json
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # Log the received event
    logger.info("Received 2nd event: " + json.dumps(event))
    
    # Add some data from Lambda 2
    event['lambda2'] = 'Hello from Lambda 2'
    
    # Log the modified event
    logger.info("Modified 2nd event: " + json.dumps(event))
    
    return event