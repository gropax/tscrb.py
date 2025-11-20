import os
from enum import Enum
from mistralai import Mistral
from openai import OpenAI


class MistralModel(str, Enum):
    voxtral_mini = "voxtral-mini-latest"
    voxtral_small = "voxtral-small-latest"


class OpenAIModel(str, Enum):
    gpt4o_mini = "gpt-4o-mini-transcribe"
    gpt4o = "gpt-4o-transcribe"
    whisper1 = "whisper-1"



class Transcriber:
    pass


class MistralTranscriber(Transcriber):
    def __init__(self, api_key):
        self.client = Mistral(api_key)

    def transcribe(self, model, audio, language=None):
        res = self.client.audio.transcriptions.complete(
            model=model,
            file={
                "content": audio,
                "file_name": "audio.mp3",
            },
            language=language)

        return res.text


class OpenAITranscriber(Transcriber):
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def transcribe(self, model, audio, language=None):
        res = self.client.audio.transcriptions.create(
            model=model,
            file=audio,
            language=language
        )

        return res.text
