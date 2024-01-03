from typing import List
from pydantic import BaseModel

from enums import DifficultyLevel


# Used to create a choice for question.
class ChoiceType(BaseModel):
    text: str
    is_answer: bool = None


# Used to create a question
class QuestionType(BaseModel):
    id: int = None
    text: str
    subdomain: str
    explanation: str = None
    snippet: str = None
    level: DifficultyLevel
    choices: List[ChoiceType] = []


# Used to create choices for a question
class ChoicesType(BaseModel):
    choices: list[ChoiceType]


class ChoiceReadType(BaseModel):
    id: int
    text: str


class QuestionReadType(BaseModel):
    id: int
    text: str
    snippet: str | None = None
    explanation: str | None = None
    choices: list[ChoiceReadType]
    # If the user has already answered this question, then populate user_answer_id
    user_answer_id: int | None = None
    correct_answer_id: int | None = None


# Used to create an user
class RegisterUser(BaseModel):
    email: str
    password: str


# Used to allow users to answer a question
class UserAnswerType(BaseModel):
    question_id: int
    choice_id: int


class UserAnswerTypeBulk(BaseModel):
    answers: list[UserAnswerType]
