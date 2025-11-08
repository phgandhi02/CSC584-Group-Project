"""
Module for generating schema for PCG based on user text input. The LLM will be
prompted with the use's text and a schema for the desired JSON output. Its 
task is to translate qualitative descriptions (e.g., ”scary,” ”open,” 
”treasure-filled”) into a quantitative set of parameters. For example, the 
input ”a dark, claustrophobic dungeon” might yield the following JSON:

    {"corridor width": 0.2,
    "room density": 0.8,
    "light sources": 0.1,"enemy density": 0.6}

"""

from dataclasses import dataclass
from typing import TypedDict, Required, Literal, Annotated

from ollama import chat  # type: ignore
from pydantic import BaseModel, StringConstraints


class Layout(TypedDict, total=False):
    """TypedDict for representing layout params of PCG.

    Args:
        TypedDict ({"map_width":int, "map_height":int}): Basic elements necessary to do PCG
    """

    map_width: Required[int]
    map_height: Required[int]


class Aesthetic(TypedDict):
    """TypedDict for representing layout params of PCG.

    Args:
        TypedDict ({"theme":str}): Basic elements necessary to do PCG
    """

    single_word_theme: Annotated[str, StringConstraints(min_length=3, max_length=20)]


@dataclass
class Level(BaseModel):
    """
    Minimal class for PCG level.
    """

    layout: Layout  # dict[str, Any]
    aesthetic: Aesthetic
    algorithm: Literal["genetic", "RNG", "grammar"]


response = chat(
    model="gemma3",
    messages=[
        {
            "role": "user",
            "content": "Design a rogue-like level. Don't include optional parameters.",
        }
    ],
    format=Level.model_json_schema(),
)

if response.message.content:
    level = Level.model_validate_json(response.message.content)
    print(level)
