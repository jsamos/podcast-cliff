import json
from lib.queue import q
import os
from lib.events import Events

def fragment_list_completed(json_string):
    item_dict = json.loads(json_string)
    full_length_path = item_dict['files']['full_length']
    episode_folder = os.path.dirname(full_length_path)
    filename_without_ext = os.path.splitext(os.path.basename(full_length_path))[0]
    transcript_file_path = os.path.join(episode_folder, f"{filename_without_ext}_transcript.txt")

    with open(transcript_file_path, 'w') as transcript_file:
        for fragment in item_dict['files']['fragments']:
            start_time = fragment['start']
            end_time = fragment['end']
            transcript_file.write(f">>TIME: {start_time}, {end_time}\n")
            transcript_path = fragment['transcript_path']
            with open(transcript_path, 'r') as fragment_file:
                transcript_file.write(fragment_file.read() + "\n")

    item_dict['files']['transcript_file_path'] = transcript_file_path
    print(f"Combined transcript saved: {transcript_file_path}")
    Events.fire('transcript_file_saved', item_dict)
    json_output = json.dumps(item_dict)
    q.enqueue('file.transcript_file_saved', json_output)

def transcript_file_saved(json_string):
    item_dict = json.loads(json_string)
    files = item_dict['files']
    full_length_path = files['full_length']
    fragments = files['fragments']
    fragment_files = [fragment['path'] for fragment in fragments]
    fragment_transcript_files = [fragment['transcript_path'] for fragment in fragments]

    for file_path in [full_length_path] + fragment_files + fragment_transcript_files:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted file: {file_path}")
        else:
            print(f"File not found, could not delete: {file_path}")

    print("All temporary files deleted, final transcript preserved.")