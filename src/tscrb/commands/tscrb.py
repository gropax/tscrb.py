import sys
import os
import typer
from enum import Enum
from pathlib import Path
from tscrb.utils import get_api_key
from tscrb.transcription import (
    MistralModel,
    OpenAIModel,
    TranscriptionModel,
    get_model,
    get_transcriber
)


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
        None, "-M", "--mistral", help=f"Use Mistral (default model: {MistralModel.DEFAULT.value})."
    ),
    use_openai: bool = typer.Option(
        None, "-O", "--openai", help=f"Use OpenAI (default model: {OpenAIModel.DEFAULT.value})."
    ),
    use_model: TranscriptionModel | None = typer.Option(
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
