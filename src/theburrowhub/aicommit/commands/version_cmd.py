import json

import click

from theburrowhub.aicommit.__version__ import __version__
from theburrowhub.aicommit.cli import console


@click.command()
@click.option("--format", "-f", default="text", type=click.Choice(["text", "json"]),
              help="Output format. Default is text. Available options are text and JSON.")
def version(format: str):
    version_value = __version__ if format == "text" else json.dumps({"version": __version__})

    console.print(version_value)
