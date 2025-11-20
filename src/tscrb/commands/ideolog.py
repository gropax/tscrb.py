import sys
from pathlib import Path
import typer
from typing_extensions import Annotated
from tscrb.utils import get_api_key
from tscrb.chat import (
    MistralModel,
    OpenAIModel,
    AIModel,
    get_model,
    get_client
)


app = typer.Typer(help="Ideological analysis tool based on chat bots.")

system_prompt = "Fait une analyse idéologique du texte fourni. Retourne ta réponse formattée en Markdown directement (pas dans un bloc ```)."

@app.command("analyze")
def command(
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
    use_model: AIModel | None = typer.Option(
        None, "-m", "--model", help="Use a specific chat model.",
    ),
    dry_run: bool = typer.Option(
        False, "-d", "--dry-run", help="Show transcription params."
    ),
    verbose: bool = typer.Option(
        False, "-v", "--verbose", help="Display more logs."
    ),
):
    (provider, model) = get_model(use_mistral, use_openai, use_model)
    (api_key, api_key_file) = get_api_key(provider, api_key_file)
    client = get_client(provider, api_key)

    if dry_run or verbose:
        typer.echo("=" * 80, err=True)
        typer.echo(f"Provider: {provider.value}", err=True)
        typer.echo(f"Model: {model}", err=True)
        typer.echo(f"API key: {api_key_file}", err=True)
        typer.echo("=" * 80, err=True)

    if dry_run:
        return

    user_prompt = sys.stdin.read()

    res = client.send(model, system_prompt, user_prompt)

    if output_path:
        output_path.write(res)
    else:
        sys.stdout.write(res)



def main():
    app()
