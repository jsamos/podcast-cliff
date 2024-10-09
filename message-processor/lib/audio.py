from abc import ABC, abstractmethod
import os
from pydub import AudioSegment
import boto3
from io import BytesIO
import logging
from lib.files import S3URI

# Add this logger configuration
logger = logging.getLogger()
logger.setLevel(logging.INFO)

class AudioFileManager(ABC):
    @abstractmethod
    def load_audio(self):
        pass

    @abstractmethod
    def save_fragment(self, fragment, fragment_path):
        pass

class LocalAudioFileManager(AudioFileManager):
    def __init__(self, file_path):
        self.file_path = file_path

    def load_audio(self):
        return AudioSegment.from_mp3(self.file_path).set_frame_rate(16000)

    def save_fragment(self, fragment, fragment_path):
        fragment.export(fragment_path, format="wav")
        return fragment_path

class S3AudioFileManager(AudioFileManager):
    def __init__(self, s3_uri):
        self.uri = S3URI(s3_uri)
        self.s3_client = boto3.client('s3')

    def load_audio(self):
        response = self.s3_client.get_object(Bucket=self.uri.bucket, Key=self.uri.key)
        audio_data = response['Body'].read()
        logger.info(f"Audio data loaded from S3")
        return AudioSegment.from_mp3(BytesIO(audio_data)).set_frame_rate(16000)

    def save_fragment(self, fragment, name):
        key = self.uri.prefix + '/' + name
        self.s3_client.put_object(
            Bucket=self.uri.bucket,
            Key=key,
            Body=fragment.export(format="wav").read()
        )

        return f"s3://{self.uri.bucket}/{key}"

def create_audio_fragments(audio_manager, fragment_length):
    logger.info("Processing audio file")

    audio = audio_manager.load_audio()
    duration = len(audio) // 1000

    logger.info(f"Audio duration (seconds): {duration}")

    fragments = []
    fragment_length_ms = fragment_length * 1000

    for i, start in enumerate(range(0, len(audio), fragment_length_ms)):
        end = min(start + fragment_length_ms, len(audio))
        fragment = audio[start:end]
        fragment_name = f"{start // 1000}_{end // 1000}.wav"
        save_uri = audio_manager.save_fragment(fragment, fragment_name)
        logger.info(f"Created fragment: {save_uri}")

        fragment_metadata = {
            'index': i + 1, 
            'start': start // 1000, 
            'end': end // 1000, 
            'path': save_uri
        }

        fragments.append(fragment_metadata)

    return fragments

def add_transcript_path(dicts):
    for i in range(len(dicts)):
        dicts[i]['transcript_path'] = f"{dicts[i]['path']}.txt"
    return dicts