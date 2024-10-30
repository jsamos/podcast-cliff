import json
from youtube_transcript_api import YouTubeTranscriptApi
import urllib.parse
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def extract_video_id(url_or_id):
    logger.info(f"Extracting video ID from {url_or_id}")
    if url_or_id.startswith('http://') or url_or_id.startswith('https://'):
        logger.info(f"URL detected, parsing")
        parsed_url = urllib.parse.urlparse(url_or_id)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        video_id = query_params.get('v', [None])[0]
        if video_id:
            return video_id
    return url_or_id

def fetch_transcript(url_or_id):
    video_id = extract_video_id(url_or_id)
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    return transcript
