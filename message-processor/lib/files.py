import os
import time
from lib.events import Events

class FileWaiter:
    def __init__(self, job_id, max_wait_time, check_interval):
        self.job_id = job_id
        self.max_wait_time = max_wait_time
        self.check_interval = check_interval

    def wait_for_files(self, expected_files):
        start_time = time.time()

        while True:
            existing_files_count = sum(1 for file in expected_files if os.path.exists(file))
            all_files_exist = existing_files_count == len(expected_files)

            if all_files_exist:
                print(f"All expected files found for job {self.job_id}")
                return True
            elif time.time() - start_time > self.max_wait_time:
                print(f"Timeout occurred after waiting for {self.max_wait_time} seconds for job {self.job_id}.")
                return False
            else:
                Events.fire('transcription_in_progress', {'job_id': self.job_id, 'progress': existing_files_count/len(expected_files)})
                print(f"Waiting for files for job {self.job_id}. Checking again in {self.check_interval} seconds.")
                time.sleep(self.check_interval)

def add_transcript_path(dicts):
    for i in range(len(dicts)):
        dicts[i]['transcript_path'] = f"{dicts[i]['path']}.txt"
    return dicts

def create_media_folder(folder):
    download_folder = "/data"
    media_folder = os.path.join(download_folder, folder)
    os.makedirs(media_folder, exist_ok=True)
    return media_folder

def save_streamed_media(response, path):
    with open(path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)
    print(f"Media downloaded successfully: {path}")