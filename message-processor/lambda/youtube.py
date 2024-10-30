import json
from youtube_transcript_api import YouTubeTranscriptApi
from lib.youtube import fetch_transcript


def transcript(event, context):
    body = json.loads(event['body'])
    id_url = body.get('id_url')
    
    if not id_url:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'id_url is required'})
        }
    
    transcript = fetch_transcript(id_url)

    return {
        'statusCode': 200,
        'body': json.dumps(transcript)
    }
