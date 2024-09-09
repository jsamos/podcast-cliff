import json
import speech_recognition as sr
from vosk import Model, KaldiRecognizer, SetLogLevel

SetLogLevel(-1)

model_path = "vosk-model-small-en-us-0.15"
model = Model(model_path)

def transcribe_audio(audio_path):
    recognizer = sr.Recognizer()

    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)

    rec = KaldiRecognizer(model, 16000)
    rec.AcceptWaveform(audio_data.get_wav_data())

    result = json.loads(rec.Result())
    transcription = result.get('text', '')

    return transcription