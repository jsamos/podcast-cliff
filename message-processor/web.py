import json
import requests
from urllib.parse import urlparse
import os
from lib.files import create_media_folder, save_streamed_media
from lib.events import Events

def media_download_requested(json_string):
    item_dict = json.loads(json_string)
    media_url = item_dict['url']

    if not media_url:
        print("Media URL not found in the item.")
        return

    filename = os.path.basename(urlparse(media_url).path)
    media_folder = create_media_folder(filename[:-4])
    download_path = os.path.join(media_folder, filename)
    Events.fire('media_dowloading', item_dict)
    response = requests.get(media_url, stream=True)

    if response.status_code != 200:
        print(f"Failed to download episode. Status code: {response.status_code}")
    else:
        save_streamed_media(response, download_path)
        item_dict['files'] = {'full_length': download_path}
        Events.fire('media_download_completed', item_dict)