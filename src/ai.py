from openai import OpenAI
from .api.models import Message
from dataclasses import dataclass


@dataclass
class Usage:
    input_tokens: int
    output_tokens: int


@dataclass
class ChatResponse:
    response: str
    usage: Usage


def chat(messages: list[Message]) -> ChatResponse:

    messages = [{"role": m.role, "content": m.content} for m in messages]
    res = OpenAI().chat.completions.create(
        messages=messages,
        model="gpt-4o-mini",
    )
    return ChatResponse(
        response=res.choices[0].message.content,
        usage=Usage(
            input_tokens=res.usage.prompt_tokens,
            output_tokens=res.usage.completion_tokens,
        ),
    )
