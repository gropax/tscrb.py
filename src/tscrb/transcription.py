import os
from enum import Enum
from mistralai import Mistral
from openai import OpenAI
from tscrb.utils import AIProvider, create_model_getter


class MistralModel(str, Enum):
    voxtral_mini = "voxtral-mini-latest"
    voxtral_small = "voxtral-small-latest"
    DEFAULT = voxtral_mini


class OpenAIModel(str, Enum):
    gpt4o_mini = "gpt-4o-mini-transcribe"
    gpt4o = "gpt-4o-transcribe"
    whisper1 = "whisper-1"
    DEFAULT = gpt4o_mini


class TranscriptionModel(str, Enum):
    voxtral_mini = MistralModel.voxtral_mini.value
    voxtral_small = MistralModel.voxtral_small.value
    gpt4o_mini = OpenAIModel.gpt4o_mini.value
    gpt4o = OpenAIModel.gpt4o.value
    whisper1 = OpenAIModel.whisper1.value
    DEFAULT = voxtral_mini


get_model = create_model_getter(MistralModel, OpenAIModel)



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



def get_transcriber(provider, api_key):
    if provider == AIProvider.mistral:
        return MistralTranscriber(api_key)
    elif provider == AIProvider.openai:
        return OpenAITranscriber(api_key)
    else:
        raise
