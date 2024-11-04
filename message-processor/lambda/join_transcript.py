import lib.storage as storage

def lambda_handler(event, context):
    fragments = sorted(event['data']['files']['fragments'], key=lambda x: x['index'])
    transcript_parts = [storage.fetch_transcript_fragment(fragment['transcript']) for fragment in fragments]
    transcript = " ".join(transcript_parts)
    content_key = event['metadata']['storage']
    storage.put_transcript(content_key, transcript)
    event['metadata']['steps'].append('TranscriptStored')
    return event