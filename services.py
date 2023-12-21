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

from orm.models import Choice, Question
from orm.engine import get_engine

from enums import OrderDirection, DifficultyLevel


def create_question_choices(question_id: int, choices):
    INVALID_QUESTION_ID = "Invalid question id"
    engine = get_engine()
    with Session(engine) as session:
        question = session.get(Question, question_id)
        if question is None:
            # Session will be closed, context manager will ensure that
            # https://stackoverflow.com/questions/9885217/in-python-if-i-return-inside-a-with-block-will-the-file-still-close
            return False, INVALID_QUESTION_ID
        for choice in choices:
            instance = Choice(question_id=question_id, text=choice.text, is_answer=choice.is_answer)
            try:
                session.add(instance)
                session.commit()
            except Exception as exc:
                session.rollback()
                raise exc
    return True, ''


def read_question(pk: int) -> Question:
    engine = get_engine()
    statement = select(Question).options(selectinload(Question.choices)).where(Question.id == pk)
    with Session(engine) as session:
        question = session.scalar(statement)
    return question


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
        result = session.execute(statement)
        questions = result.scalars().all()
    return questions


def create_instance(model, data: dict) -> int:
    engine = get_engine()
    instance = model(**data)
    created_id = None
    with Session(engine) as session:
        try:
            session.add(instance)
            session.commit()
            created_id = instance.id
        except Exception as exc:
            session.rollback()
            raise exc
    return created_id
