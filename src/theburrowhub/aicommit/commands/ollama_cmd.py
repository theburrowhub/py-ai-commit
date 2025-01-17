import click
import ollama as ollama_api
from rich.prompt import Prompt
from rich.table import Table

from theburrowhub.aicommit.cli import console, error_console


@click.group
def ollama():
    """
    Group of commands for interacting with the Ollama API,
    including model management and other operations.
    """


@click.group()
def model():
    """
    Commands for managing Ollama models, such as listing available models,
    adding new models, and deleting existing models.
    """


@click.command()
def list():
    """
    List available Ollama models.
    """
    try:
        results = ollama_api.list()
    except Exception as e:
        error_console.print(e)
        return

    table = Table(title="Ollama models")
    table.add_column("Model")
    table.add_column("Format")
    table.add_column("Parameter Size")
    table.add_column("Quantization Level")
    table.add_column("Modified")

    for model in results.models:
        table.add_row(
                model.model,
                model.details.format,
                model.details.parameter_size,
                model.details.quantization_level,
                str(model.modified_at),
        )

    console.print(table)


@click.command()
@click.argument("model", type=str)
def show(model: str):
    """
    Show details for a specific model.
    """
    try:
        result = ollama_api.show(model)
        console.print(result)
    except Exception as e:
        error_console.print(e)


@click.command()
@click.argument("model", type=str)
def pull(model: str):
    """
    Pull the latest version of a model.
    """
    try:
        ollama_api.pull(model)
        console.print(f"Model '{model}' pulled successfully.", style="bold green")
    except Exception as e:
        error_console.print(e)


@click.command()
@click.argument("model", type=str)
def delete(model: str):
    """
    Delete a model.
    """
    try:
        ollama_api.delete(model)
        console.print(f"Model '{model}' deleted successfully.", style="bold green")
    except Exception as e:
        error_console.print(e)


@click.command()
@click.argument("model", type=str)
def generate(model: str):
    """
    Runs a prompt to a given model.
    """
    prompt = Prompt.ask("Prompt")

    try:
        result = ollama_api.generate(model, prompt)
    except Exception as e:
        error_console.print(e)
        return

    console.print(result.response)


ollama.add_command(model)
model.add_command(list)
model.add_command(show)
model.add_command(pull)
model.add_command(delete)
ollama.add_command(generate)

ollama_cmd = ollama
