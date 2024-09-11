from lib.files import FileWaiter
from lib.queue import q
import json
from config import TRANSCRIPTION_CHECK_INTERVAL, TRANSCRIPTION_MAX_WAIT_TIME
from lib.events import Events

def file_list_enqueued(json_string):
    item_dict = json.loads(json_string)
    expected_files = [fragment['transcript_path'] for fragment in item_dict['files']['fragments']]
    file_waiter = FileWaiter(item_dict['job_id'], TRANSCRIPTION_MAX_WAIT_TIME, TRANSCRIPTION_CHECK_INTERVAL)
    files_found = file_waiter.wait_for_files(expected_files)
    
    if files_found:
        print(f"All transcription files found")
        Events.fire('transcription_fragments_created', item_dict)
    else:
        print(f"Transcription timeout occurred.")