import json
import logging
import lib.storage as storage
import lib.llm as llm

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    content_key = event['metadata']['storage']        
    transcript = storage.get_transcript(content_key)
    ebook_content = llm.generate_ebook(transcript)
    logger.info(f"Ebook generated successfully: {ebook_content}")
    storage.put_ebook(content_key, ebook_content)
    logger.info(f"Ebook stored with key: {content_key}")        
    event['metadata']['steps'].append('EbookGenerated')
    logger.info(f"Event after update: {event}")

    return event
