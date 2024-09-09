import os
from pydub import AudioSegment

def create_audio_fragments(full_length_path, fragment_length):
    print(f"Processing full length audio file: {full_length_path}")

    audio = AudioSegment.from_mp3(full_length_path).set_frame_rate(16000)
    duration = len(audio) // 1000

    print(f"Audio duration (seconds): {duration}")

    fragments = []
    fragment_length_ms = fragment_length * 1000

    for i, start in enumerate(range(0, len(audio), fragment_length_ms)):
        end = min(start + fragment_length_ms, len(audio))
        fragment = audio[start:end]
        fragment_path = f"{os.path.splitext(full_length_path)[0]}_{start // 1000}_{end // 1000}.wav"
        fragment.export(fragment_path, format="wav")
        print(f"Created fragment: {fragment_path}")
        fragment_metadata = {
            'index': i + 1, 
            'start': start // 1000, 
            'end': end // 1000, 
            'path': fragment_path
        }
        fragments.append(fragment_metadata)

    return fragments

def add_transcript_path(dicts):
    for i in range(len(dicts)):
        dicts[i]['transcript_path'] = f"{dicts[i]['path']}.txt"
    return dicts