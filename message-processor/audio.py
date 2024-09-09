from lib.transcription import transcribe_audio
from lib.audio import create_audio_fragments
from lib.files import add_transcript_path
from lib.queue import q
from config import AUDIO_FRAGMENT_LENGTH
import json

def fragment_saved(json_string):
    fragment_dict = json.loads(json_string)
    transcription = transcribe_audio(fragment_dict['path'])

    with open(fragment_dict['transcript_path'], 'w') as file:
        file.write(transcription)

    print(f"Transcription saved: {fragment_dict['transcript_path']}")

def new_file_present(json_string):
    item_dict = json.loads(json_string)
    full_length_path = item_dict['files']['full_length']
    item_dict['files']['fragments'] = create_audio_fragments(full_length_path, AUDIO_FRAGMENT_LENGTH)
    add_transcript_path(item_dict['files']['fragments'])

    for fragment in item_dict['files']['fragments']:
        q.enqueue('audio.fragment_saved', json.dumps(fragment))

    json_output = json.dumps(item_dict)
    q.enqueue('pending.file_list_enqueued', json_output)