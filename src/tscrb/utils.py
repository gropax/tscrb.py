import os
from enum import Enum
from pathlib import Path


class AIProvider(str, Enum):
    mistral = "Mistral"
    openai = "OpenAI"


def is_known_model(provider, model):
    return model.value in (m.value for m in provider)


def get_api_key(provider, api_key_file):
    if api_key_file:
        f = api_key_file
    elif provider == AIProvider.mistral:
        f = os.environ.get("MISTRAL_API_KEY_FILE")
    elif provider == AIProvider.openai:
        f = os.environ.get("OPENAI_API_KEY_FILE")
    else:
        raise

    api_key = Path(f).read_text().strip()

    return (api_key, f)


def create_model_getter(mistral_models, openai_models):
    def get_model(use_mistral, use_openai, use_model):
        if use_mistral and use_openai:
            raise typer.BadParameter(f"Multiple AI provider specified.")
        elif not (use_mistral or use_openai or use_model):
            use_mistral = True

        if use_mistral:
            provider = AIProvider.mistral
            if not use_model:
                model = mistral_models.DEFAULT
            elif is_known_model(mistral_models, use_model):
                model = use_model
            else:
                raise typer.BadParameter(f"Unknown Mistral model: {use_model}.")

        elif use_openai:
            provider = AIProvider.openai
            if not use_model:
                model = openai_models.DEFAULT
            elif is_known_model(openai_models, use_model):
                model = use_model
            else:
                raise typer.BadParameter(f"Unknown OpenAI model: {use_model}.")

        elif use_model:
            if is_known_model(mistral_models, use_model):
                provider = AIProvider.mistral
            elif is_known_model(openai_models, use_model):
                provider = AIProvider.openai
            else:
                raise typer.BadParameter(f"Unknown model: {use_model}.")

            model = use_model

        return (provider, model.value)

    return get_model
