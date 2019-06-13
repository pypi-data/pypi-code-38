from dataclasses import dataclass


@dataclass(frozen=True)
class Message:
    title: str = ""
    subtitle: str = ""
    content: str = ""

