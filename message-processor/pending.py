from lib.files import wait_for_files
from lib.queue import q
import json
from config import TRANSCRIPTION_CHECK_INTERVAL, TRANSCRIPTION_MAX_WAIT_TIME

def file_list_enqueued(json_string):
    item_dict = json.loads(json_string)
    expected_files = [fragment['transcript_path'] for fragment in item_dict['files']['fragments']]
    files_found = wait_for_files(expected_files, TRANSCRIPTION_MAX_WAIT_TIME, TRANSCRIPTION_CHECK_INTERVAL)
    
    if files_found:
        print(f"All transcription files found")
        q.enqueue('file.fragment_list_completed', json_string)
    else:
        print(f"Transcription timeout occurred.")