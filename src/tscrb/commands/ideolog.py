import sys
from pathlib import Path
import functools
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


output_opt = typer.Option(
    None, "-o", "--output",
    help="Output file (default: stdout)."
)

api_key_file_opt = typer.Option(
    None, "-k", "--api-key",
    help="File containing the API key."
)

use_mistral_opt = typer.Option(
    None, "-M", "--mistral",
    help=f"Use Mistral (default model: {MistralModel.DEFAULT.value})."
)

use_openai_opt = typer.Option(
    None, "-O", "--openai",
    help=f"Use OpenAI (default model: {OpenAIModel.DEFAULT.value})."
)

use_model_opt = typer.Option(
    None, "-m", "--model",
    help="Use a specific chat model."
)

dry_run_opt = typer.Option(
    False, "-d", "--dry-run",
    help="Show transcription params."
)

verbose_opt = typer.Option(
    False, "-v", "--verbose",
    help="Display more logs."
)


@app.command("analyze")
def command(
    output: typer.FileTextWrite | None = output_opt,
    api_key_file: str | None = api_key_file_opt,
    use_mistral: bool = use_mistral_opt,
    use_openai: bool = use_openai_opt,
    use_model: AIModel | None = use_model_opt,
    dry_run: bool = dry_run_opt,
    verbose: bool = verbose_opt,
):
    system_prompt = """
    Fait une analyse idéologique du texte fourni.
    Retourne ta réponse formattée en Markdown directement (pas dans un bloc ```).
    """
    chat_command(output, api_key_file, use_mistral, use_openai, use_model, dry_run, verbose, system_prompt)


@app.command("terms")
def terms_command(
    output: typer.FileTextWrite | None = output_opt,
    api_key_file: str | None = api_key_file_opt,
    use_mistral: bool = use_mistral_opt,
    use_openai: bool = use_openai_opt,
    use_model: AIModel | None = use_model_opt,
    dry_run: bool = dry_run_opt,
    verbose: bool = verbose_opt,
):
    count = 5
    words = 50
    system_prompt = f"""
    - Tu es un chercheur spécialisé dans l'étude des discours philosophico-politiques.
    - Dans l'input de l'utilisateur, identifie les {count} plus importants termes et expressions (attestés dans le texte!) qui véhiculent des conceptions philosophiques et politiques implicites, et explicite en moins de {words} mots ces présupposés.
    - Retourne ta réponse formattée en Markdown directement (pas dans un bloc ```).
    - Retourne en première ligne "# Terminology"
    - Utilise des titres 2 pour chaque entrée (##) et pas des bullets points.
    - Utilise des _ au lieu des guillemets (")\
    """
    chat_command(output, api_key_file, use_mistral, use_openai, use_model, dry_run, verbose, system_prompt)



def chat_command(output, api_key_file, use_mistral, use_openai, use_model, dry_run, verbose, system_prompt):
    (provider, model) = get_model(use_mistral, use_openai, use_model)
    (api_key, api_key_file) = get_api_key(provider, api_key_file)
    client = get_client(provider, api_key)

    if dry_run or verbose:
        typer.echo("=" * 80, err=True)
        typer.echo(f"Provider: {provider.value}", err=True)
        typer.echo(f"Model: {model}", err=True)
        typer.echo(f"API key: {api_key_file}", err=True)
        typer.echo(f"Prompt:{system_prompt}", err=True)
        typer.echo("=" * 80, err=True)

    if dry_run:
        return

    user_prompt = sys.stdin.read()

    res = client.send(model, system_prompt, user_prompt)

    if output:
        output.write(res)
    else:
        sys.stdout.write(res)



def main():
    app()
