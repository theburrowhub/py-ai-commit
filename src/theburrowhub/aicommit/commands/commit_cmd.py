import os
import subprocess

import click
import git
import ollama
import pyperclip
import rich.panel
from pick import pick
from rich.prompt import Prompt

from theburrowhub.aicommit import exceptions
from theburrowhub.aicommit.cli import console, error_console
from theburrowhub.aicommit.models import Message, MessageType


def _generate_prompt(branch_name: str, diff: str) -> str:
    return (
        "You are an advanced AI model trained to generate meaningful and concise git commit messages.\n\n"
        f"Below is the git diff of the staged changes in the current repository for branch {branch_name}:\n"
        "====================================\n"
        f"{diff}\n"
        "====================================\n\n"
        "Based on the diff above, provide a concise and meaningful git commit."
        "The commit message should be structured as follows:"
        "<type>[optional scope]: <description>"
        "\n"
        "[optional body]"
        "\n"
        "[optional footer(s)]"
        "-------------------------------------"
        "The commit contains the following structural elements, to communicate intent to the consumers of your library:"
        "fix: a commit of the type fix patches a bug in your codebase (this correlates with PATCH in Semantic Versioning)."
        "feat: a commit of the type feat introduces a new feature to the codebase (this correlates with MINOR in Semantic Versioning)."
        "BREAKING CHANGE: a commit that has a footer BREAKING CHANGE:, or appends a ! after the type/scope, introduces a breaking API change (correlating with MAJOR in Semantic Versioning). A BREAKING CHANGE can be part of commits of any type."
        "types other than fix: and feat: are allowed, for example @commitlint/config-conventional (based on the Angular convention) recommends build:, chore:, ci:, docs:, style:, refactor:, perf:, test:, and others."
        "footers other than BREAKING CHANGE: <description> may be provided and follow a convention similar to git trailer format"
        "Use conventional commits and the imperative mood in the first line."
        "The first line should be less than 50 characters."
        "The body should be wrapped at 72 characters."
        "The first line should start with: feat, fix, refactor, docs, style, build, perf, ci, style, test or chore."
        "Only one subject line is allowed."
        "When there is only one file edit, use the file name in the subject line."
        "When there are multiple file edits, use the module name in the subject line."
        "When there are multiple modules edited, do not include any file/module name in the subject line."
        "Examples:"
        "fix: correct typo in README"
        "---------------------------------"
        "refactor: improve performance of the algorithm"
        "---------------------------------"
        "docs: update README"
        "---------------------------------"
        "style: format code"
        "---------------------------------"
        "build: update dependencies"
        "---------------------------------"
        "feat(main.py): add new feature to the backend"
        " - add new endpoint to the API"
        " - update the database schema"
    )


def _generate_commit_message(model: str, branch_name: str, diff: str) -> Message:
    console.print(f":robot: Generating commit message using model [reverse]{model}[/reverse]", style="bold")
    prompt = _generate_prompt(branch_name, diff)
    schema = Message.model_json_schema()
    result = ollama.chat(
            model=model,
            messages=[{'role': 'user', 'content': prompt}],
            format=schema,
            options={"temperature": 0})
    return Message.model_validate_json(result.message.content)


def _create_commit(message: Message) -> None:
    repo = git.Repo(os.curdir)
    index = repo.index
    index.commit(str(message))


def _quick_edit_message(message: Message) -> Message:
    options = ["fix", "feat", "docs", "style", "refactor", "perf", "test", "build", "ci", "chore"]
    quick_edit, _ = pick(options=options, title="Quick change type", indicator="=>")
    message.message_type = MessageType(quick_edit)
    return message


@click.command()
@click.option("-m", "--model", type=str, default="llama3.1", help="The model to use for generating the commit message")
def commit(model: str):
    console.print(":memo: Generating commit message...")
    branch_name = _get_branch_name()
    console.print(f":herb: Current branch is: {branch_name}", style="bold")
    console.print(":mag: Obtaining diff from the working directory...")

    try:
        diffs = _get_repository_diffs()
    except Exception as e:
        error_console.print(e, style="bold red")
        return

    message = _generate_commit_message(model, branch_name, diffs)
    message_str = str(message)
    panel = rich.panel.Panel(message_str, title="Commit Message", expand=False)
    console.print(panel)
    action = Prompt.ask("Commit changes? (Y)es (N)o (E)dit (Q)uick change type (C)opy",
                        choices=["y", "n", "e", "q", "c"],
                        default="y")

    if action == "y":
        _create_commit(message)

    if action == "n":
        console.print(":x: Canceled by user", style="bold red")
        return

    if action == "e":
        message_str = click.edit(message_str, editor="vim")  # todo Get editor from config

        if len(message_str) == 0:
            raise exceptions.MessageIsEmpty()  # fixme Pretty print this

        _create_commit(message)

    if action == "q":
        message = _quick_edit_message(message)
        _create_commit(message)

    if action == "c":
        pyperclip.copy(message_str)
        console.print(":clipboard: Commit message copied to clipboard", style="bold")
        return

    console.print(":tada: Commit message generated successfully!", style="bold green")


def _get_branch_name():
    return subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True).stdout.strip()


def _get_repository_diffs() -> str:
    diffs = subprocess.run(["git", "diff", "--cached"], capture_output=True, text=True, check=True).stdout.strip()
    diff_len = len(diffs)

    if diff_len == 0:
        raise exceptions.DiffIsZeroLen()

    console.print(f":receipt: Current diff message is {diff_len} chars long")
    return diffs
