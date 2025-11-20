import sys
import os
import typer
from enum import Enum
from pathlib import Path
from tscrb.transcription import MistralModel, OpenAIModel, MistralTranscriber, OpenAITranscriber


DEFAULT_MISTRAL_MODEL = MistralModel.voxtral_mini
DEFAULT_OPENAI_MODEL = OpenAIModel.gpt4o_mini

class Model(str, Enum):
    voxtral_mini = MistralModel.voxtral_mini.value
    voxtral_small = MistralModel.voxtral_small.value
    gpt4o_mini = OpenAIModel.gpt4o_mini.value
    gpt4o = OpenAIModel.gpt4o.value
    whisper1 = OpenAIModel.whisper1.value


def is_known_model(provider, model):
    return model.value in (m.value for m in provider)


def get_model(use_mistral, use_openai, use_model):
    if use_mistral and use_openai:
        raise typer.BadParameter(f"Multiple AI provider specified.")
    elif not (use_mistral or use_openai or use_model):
        use_mistral = True

    if use_mistral:
        provider = "Mistral"
        if not use_model:
            model = DEFAULT_MISTRAL_MODEL
        elif is_known_model(use_model, MistralModel):
            model = use_model
        else:
            raise typer.BadParameter(f"Unknown Mistral model: {use_model}.")

    elif use_openai:
        provider = "OpenAI"
        if not use_model:
            model = DEFAULT_OPENAI_MODEL
        elif is_known_model(use_model, OpenAIModel):
            model = use_model
        else:
            raise typer.BadParameter(f"Unknown OpenAI model: {use_model}.")

    elif use_model:
        if is_known_model(use_model, MistralModel):
            provider = "Mistral"
        elif is_known_model(use_model, OpenAIModel):
            provider = "OpenAI"
        else:
            raise typer.BadParameter(f"Unknown model: {use_model}.")

        model = use_model

    return (provider, model.value)


def get_api_key(provider, api_key_file):
    if api_key_file:
        f = api_key_file
    elif provider == "Mistral":
        f = os.environ.get("MISTRAL_API_KEY_FILE")
    elif provider == "OpenAI":
        f = os.environ.get("OPENAI_API_KEY_FILE")
    else:
        raise

    api_key = Path(f).read_text().strip()

    return (api_key, f)


def get_transcriber(provider, api_key):
    if provider == "Mistral":
        return MistralTranscriber(api_key)
    elif provider == "OpenAI":
        return OpenAITranscriber(api_key)
    else:
        raise



app = typer.Typer(help="tscrb audio transcription tool.")

@app.command("transcribe")
def command(
    input_path: str = typer.Argument(help="Audio input file."),
    output_path: typer.FileTextWrite | None = typer.Option(
        None, "-o", "--output", help="Output file (default: stdout)."
    ),
    api_key_file: str | None = typer.Option(
        None, "-k", "--api-key", help="File containing the API key."
    ),
    use_mistral: bool = typer.Option(
        None, "-M", "--mistral", help=f"Use Mistral (default model: {DEFAULT_MISTRAL_MODEL.value})."
    ),
    use_openai: bool = typer.Option(
        None, "-O", "--openai", help=f"Use OpenAI (default model: {DEFAULT_OPENAI_MODEL.value})."
    ),
    use_model: Model | None = typer.Option(
        None, "-m", "--model", help="Use specific transcription model."
    ),
    language: str | None = typer.Option(
        None, "-l", "--language", help="Language to use for transcription."
    ),
    dry_run: bool = typer.Option(
        False, "-d", "--dry-run", help="Show transcription params."
    ),
    verbose: bool = typer.Option(
        False, "-v", "--verbose", help="Display more logs."
    ),
):
    audio_file = Path(input_path).resolve()
    (provider, model) = get_model(use_mistral, use_openai, use_model)
    (api_key, api_key_file) = get_api_key(provider, api_key_file)
    transcriber = get_transcriber(provider, api_key)

    if dry_run or verbose:
        typer.echo("=" * 80, err=True)
        typer.echo(f"Audio file: {audio_file}", err=True)
        typer.echo(f"Provider: {provider}", err=True)
        typer.echo(f"Model: {model}", err=True)
        typer.echo(f"API key: {api_key_file}", err=True)
        typer.echo("=" * 80, err=True)

    if dry_run:
        return

    with open(audio_file, "rb") as audio:
        res = transcriber.transcribe(model, audio, language)

    if output_path:
        output_path.write(res)
    else:
        sys.stdout.write(res)



def main():
    app()
