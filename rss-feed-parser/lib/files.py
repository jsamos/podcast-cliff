import os

def create_episode_folder(folder):
    download_folder = "/data"
    episode_folder = os.path.join(download_folder, folder)
    os.makedirs(episode_folder, exist_ok=True)
    return episode_folder

def save_episode(response, path):
    with open(path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)
    print(f"Episode downloaded successfully: {path}")