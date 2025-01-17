import click

from theburrowhub.aicommit.commands.commit_cmd import commit
from theburrowhub.aicommit.commands.ollama_cmd import ollama
from theburrowhub.aicommit.commands.version_cmd import version


@click.group()
def app():
    """
    AI Commit is a tool to help you write better commit messages.
    """
    pass


@click.command()
def init():
    click.echo("Initializing...")


app.add_command(commit)
app.add_command(init)
app.add_command(version)
app.add_command(ollama)

if __name__ == "__main__":
    app()
