from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class MessageType(str, Enum):
    FIX = "fix"
    FEATURE = "feat"
    DOCS = "docs"
    STYLE = "style"
    REFACTOR = "refactor"
    PERFORMANCE = "perf"
    TEST = "test"
    BUILD = "build"
    CI = "ci"
    CHORE = "chore"


class Message(BaseModel):
    message_type: MessageType = Field(description="The type of message")
    message_scope: Optional[str] = Field(
            title="scope",
            description="The scope of the message. Scope can be a unique filename, module or list of modules")
    title: str = Field(description="The title of the message")
    body: Optional[str] = Field(description="The body of the message")
    is_breaking_change: bool = False
    footer: Optional[str] = Field(
            description="The reason for breaking change when is_breaking_change is True. Must be omitted if there are no breaking changes")

    def __str__(self):

        template = "{message_type}{scope}: {title}"

        if self.body:
            template += "\n\n{body}"

        if self.is_breaking_change and self.footer:
            template += "\n\n{footer}"

        return template.format(
                message_type=self.message_type.value,
                scope=(f"({self.message_scope})" if self.message_scope and self.message_scope.strip() else ""),
                title=self.title.lower(),
                body=self.body,
                footer=(self.footer if not self.is_breaking_change else f"BREAKING CHANGE: {self.footer}"),
        )
