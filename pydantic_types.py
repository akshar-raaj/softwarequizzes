from typing import List
from pydantic import BaseModel

from enums import DifficultyLevel


class ChoiceType(BaseModel):
    text: str
    is_answer: bool = None


class QuestionType(BaseModel):
    id: int = None
    text: str
    subdomain: str
    explanation: str
    level: DifficultyLevel
    choices: List[ChoiceType] = []


class ChoicesType(BaseModel):
    choices: list[ChoiceType]
