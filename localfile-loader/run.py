import argparse
import os
from bs4 import BeautifulSoup
from redis import Redis
from rq import Queue

# Establish Redis connection and queue
redis_conn = Redis(host='redis', port=6379)
q = Queue(connection=redis_conn)

def create_xml(filepath):
    # Extract the episode title from the file path
    episode_title = os.path.basename(filepath).replace('.mp3', '').replace('-', ' ')

    # Create the XML structure
    soup = BeautifulSoup(features='xml')
    item_tag = soup.new_tag('item')

    title_tag = soup.new_tag('title')
    title_tag.string = episode_title
    item_tag.append(title_tag)

    files_tag = soup.new_tag('files')
    full_length_tag = soup.new_tag('full_length')
    full_length_tag.string = filepath
    files_tag.append(full_length_tag)
    item_tag.append(files_tag)

    encoded_tag = soup.new_tag('encoded')
    encoded_tag.string = "Episode summary content"
    item_tag.append(encoded_tag)

    soup.append(item_tag)

    return str(soup)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create XML for an episode")
    parser.add_argument('filepath', type=str, help='Path to the audio file')
    args = parser.parse_args()

    xml_output = create_xml(args.filepath)
    print(xml_output)

    # Enqueue the XML document for further processing
    q.enqueue('tasks.process_local_audio', xml_output)