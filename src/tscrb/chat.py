import os
from enum import Enum
from mistralai import Mistral
from openai import OpenAI
from tscrb.utils import AIProvider, create_model_getter


class MistralModel(str, Enum):
    mistral_small = "mistral-small-latest"
    mistral_medium = "mistral-medium-latest"
    DEFAULT = mistral_small


class OpenAIModel(str, Enum):
    gpt5_nano = "gpt-5-nano"
    gpt5_mini = "gpt-5-mini"
    gpt5_1 = "gpt-5.1"
    DEFAULT = gpt5_nano


class AIModel(str, Enum):
    mistral_small = MistralModel.mistral_small.value
    mistral_medium = MistralModel.mistral_medium.value

    gpt5_nano = OpenAIModel.gpt5_nano.value
    gpt5_mini = OpenAIModel.gpt5_mini.value
    gpt5_1 = OpenAIModel.gpt5_1.value

    DEFAULT = mistral_medium


get_model = create_model_getter(MistralModel, OpenAIModel)



class ChatClient:
    pass


class MistralClient(ChatClient):
    def __init__(self, api_key):
        self.client = Mistral(api_key)

    def send(self, model, system_prompt, user_prompt):
        response = self.client.chat.complete(
            model=model,
            messages = [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ]
        )

        return response.choices[0].message.content


class OpenAIClient(ChatClient):
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def send(self, model, system_prompt, user_prompt):
        response = self.client.responses.create(
            model=model,
            instructions=system_prompt,
            input=user_prompt,
        )

        return response.output_text



def get_client(provider, api_key):
    if provider == AIProvider.mistral:
        return MistralClient(api_key)
    elif provider == AIProvider.openai:
        return OpenAIClient(api_key)
    else:
        raise
