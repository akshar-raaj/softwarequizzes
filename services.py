"""
Any new function added here must follow the naming convention of CRUD.

If a function inserts rows in the database, it's name should be create_*.
For select row, it's name should be read_*.
For select multiple rows, it's name should be list_*.
For update rows, it's name should be update_*.
For delete rows, it's name should be delete_*.
"""
import json
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from orm.engine import get_engine
from orm.models import Base, Choice, Question, User, UserAnswer
from orm.queries import list_questions as list_questions_query
from orm.queries import read_user as read_user_query

from pydantic_types import UserAnswerType, UserAnswerTypeBulk, QuestionReadType, ChoiceReadType, ChoiceWriteType

from constants import PLACEHOLDER_USER_EMAIL
from cache import set_string, get_string


def create_question_choices(question_id: int, choices: list[ChoiceWriteType]) -> tuple[bool, str]:
    INVALID_QUESTION_ID = "Invalid question id"
    ERROR_MESSAGE = "Something is wrong"
    engine = get_engine()
    with Session(engine) as session:
        question = session.get(Question, question_id)
        if question is None:
            # Session will be closed, context manager will ensure that
            # https://stackoverflow.com/questions/9885217/in-python-if-i-return-inside-a-with-block-will-the-file-still-close
            return False, INVALID_QUESTION_ID
        for choice in choices:
            instance = Choice(question_id=question_id, text=choice.text, is_answer=choice.is_answer)
            session.add(instance)
        try:
            # session.flush() automatically happens on invoking commit().
            session.commit()
        except Exception as exc:
            # No need to explicitly call session.rollback(). It happens in case we are returning without commit.
            # logger.error() is the right candidate to be used here.
            print(exc)
            return False, ERROR_MESSAGE
    return True, ''


def read_question(pk: int) -> Question:
    engine = get_engine()
    statement = select(Question).options(selectinload(Question.choices)).where(Question.id == pk)
    with Session(engine) as session:
        question = session.scalars(statement).first()
    return question


def read_user(email: str = None, pk: int = None) -> User:
    # XOR
    if not (bool(email) != bool(pk)):
        raise AssertionError('Either email or id should be provided. Both should not be provided.')
    user = read_user_query(email, pk)
    return user


def list_questions(**kwargs) -> list[QuestionReadType]:
    """
    We want to avoid calls to the database. Caching provides the following benefits:
    1. Reduce database load and hence allowing the database to handle more load.
    2. Reduce the response time from the application by reducing calls to the database.

    This method performs the following:
    1. Retrieve questions from the database.
    2. Cache the questions with an expiration time
    3. Retrieve questions from the cache if present in cache.

    We are performing query caching with cache-aside. It's not read-through or write-through.
    """
    subdomain = kwargs.get("subdomain") or ""
    difficulty_level = kwargs.get("difficulty_level")
    difficulty_level = (difficulty_level and difficulty_level.name) or ""
    limit = kwargs.get("limit", "")
    offset = kwargs.get("offset", "")
    order_by = kwargs.get("order_by", "")
    order_direction = kwargs.get("order_direction")
    order_direction = (order_direction and order_direction.name) or ""
    key = f'questions:{subdomain}:{difficulty_level}:{order_by}:{order_direction}:{limit}:{offset}'
    dumped = get_string(key)
    if dumped:
        question_type_list = json.loads(dumped)
        question_types = [QuestionReadType(**each) for each in question_type_list]
        return question_types
    questions = list_questions_query(**kwargs)
    # The above is a SQLAlchemy Question instances and cannot be serialized. Thus convert it to Pydantic type which is easier to serialize.
    question_types = []
    for question in questions:
        choice_types = []
        for choice in question.choices:
            choice_type = ChoiceReadType(id=choice.id, text=choice.text)
            choice_types.append(choice_type)
        qr = QuestionReadType(id=question.id, text=question.text, snippet=question.snippet, explanation=question.explanation, choices=choice_types)
        question_types.append(qr)
    model_dump_list = [qt.model_dump() for qt in question_types]
    set_string(key, json.dumps(model_dump_list), expire=5*60)
    return question_types


def create_instance(model: Base, data: dict) -> int:
    engine = get_engine()
    instance = model(**data)
    created_id = None
    with Session(engine) as session:
        session.add(instance)
        try:
            session.commit()
            created_id = instance.id
        except Exception as exc:
            # Possible due to invalid data being passed. Example: A non-nullable column is passed as None.
            # logger.error() is the right candidate to be used here.
            print(exc)
    return created_id


def create_user_answer(user: User, user_answer: UserAnswerType) -> tuple[bool, str]:
    INVALID_QUESTION_ID = "Invalid question id"
    INVALID_CHOICE_ID = "Invalid choice id"
    ERROR_MESSAGE = "Something is wrong"
    engine = get_engine()
    with Session(engine) as session:
        question = session.get(Question, user_answer.question_id)
        # TODO: Modify the filter condition to ensure this choice belongs to this question.
        choice = session.get(Choice, user_answer.choice_id)
        if question is None:
            # Session will be closed, context manager will ensure that
            # https://stackoverflow.com/questions/9885217/in-python-if-i-return-inside-a-with-block-will-the-file-still-close
            return False, INVALID_QUESTION_ID
        if choice is None:
            return False, INVALID_CHOICE_ID
        instance = UserAnswer(question_id=user_answer.question_id, choice_id=user_answer.choice_id, user_id=user.id)
        session.add(instance)
        try:
            session.commit()
        except Exception as exc:
            return False, ERROR_MESSAGE
    return True, ''


def create_user_answers(user: User, user_answers: UserAnswerTypeBulk):
    engine = get_engine()
    with Session(engine) as session:
        for user_answer in user_answers:
            instance = UserAnswer(question_id=user_answer.question_id, choice_id=user_answer.choice_id, user_id=user.id)
            session.add(instance)
        try:
            session.commit()
        except Exception as exc:
            return False, "Error"
    return True, ''


def fetch_user_answers(question_ids: list, user: User):
    """
    Given a list of question ids, find the answers given by the specified user for these questions.
    The return would be in the following form: {<question_id>: <choice_id>}.
    """
    if user.email == PLACEHOLDER_USER_EMAIL:
        return {}
    engine = get_engine()
    with Session(engine) as session:
        statement = select(UserAnswer).where(UserAnswer.question_id.in_(question_ids)).where(UserAnswer.user_id == user.id)
        result = session.scalars(statement)
        rows = result.all()
    return {row.question_id: row.choice_id for row in rows}


def fetch_correct_answers(question_ids: list):
    """
    Given a list of question ids, find the answers given by the specified user for these questions.
    The return would be in the following form: {<question_id>: <choice_id>}.
    """
    engine = get_engine()
    with Session(engine) as session:
        statement = select(Choice).where(Choice.question_id.in_(question_ids)).where(Choice.is_answer == True)
        result = session.scalars(statement)
        rows = result.all()
    return {row.question_id: row.id for row in rows}
