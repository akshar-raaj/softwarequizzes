"""
Any new function added here must follow the naming convention of CRUD.

If a function inserts rows in the database, it's name should be create_*.
For select row, it's name should be read_*.
For select multiple rows, it's name should be list_*.
For update rows, it's name should be update_*.
For delete rows, it's name should be delete_*.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from orm.models import Choice, Question, User, UserAnswer
from orm.engine import get_engine

from pydantic_types import UserAnswerType, UserAnswerTypeBulk

from enums import OrderDirection, DifficultyLevel
from constants import PLACEHOLDER_USER_EMAIL


def create_question_choices(question_id: int, choices):
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
    engine = get_engine()
    if email is not None:
        statement = select(User).where(User.email == email)
    if pk is not None:
        statement = select(User).where(User.id == pk)
    with Session(engine) as session:
        user = session.scalars(statement).first()
    return user


def list_questions(order_by: str = Question.created_at.name, order_direction: OrderDirection = OrderDirection.DESC, limit: int = 20, offset: int = 0, subdomain: str = None, category: str = None, difficulty_level: DifficultyLevel = None):
    engine = get_engine()
    statement = select(Question).options(selectinload(Question.choices))
    if order_by and order_direction:
        order_by_column = getattr(Question, order_by)
        if order_direction == OrderDirection.ASC:
            statement = statement.order_by(order_by_column)
        elif order_direction == OrderDirection.DESC:
            statement = statement.order_by(order_by_column.desc())
    if limit:
        statement = statement.limit(limit)
    if offset:
        statement = statement.offset(offset)
    if subdomain:
        statement = statement.where(Question.subdomain == subdomain)
    if difficulty_level:
        statement = statement.where(Question.level == difficulty_level)
    with Session(engine) as session:
        result = session.scalars(statement)
        questions = result.all()
    return questions


def create_instance(model, data: dict) -> int:
    engine = get_engine()
    instance = model(**data)
    created_id = None
    with Session(engine) as session:
        session.add(instance)
        try:
            session.commit()
            created_id = instance.id
        except Exception as exc:
            pass
    return created_id


def create_user_answer(user: User, user_answer: UserAnswerType):
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
