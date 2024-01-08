from typing import List
from pydantic import BaseModel

from enums import DifficultyLevel


# Used to create a choice for question.
class ChoiceType(BaseModel):
    text: str


class ChoiceWriteType(ChoiceType):
    is_answer: bool


class ChoiceReadType(ChoiceType):
    id: int


# Used to create choices for a question
class ChoicesType(BaseModel):
    choices: list[ChoiceWriteType]


# Question base type
class QuestionType(BaseModel):
    text: str
    explanation: str | None = None
    snippet: str | None = None


# Used to create a question
class QuestionWriteType(QuestionType):
    subdomain: str
    level: DifficultyLevel


# Used to read a question
class QuestionReadType(QuestionType):
    id: int
    choices: list[ChoiceReadType]
    # If the user has already answered this question, then populate user_answer_id and correct_answer_id
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
