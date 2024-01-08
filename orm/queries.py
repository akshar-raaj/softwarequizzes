from sqlalchemy import select
from sqlalchemy.orm import selectinload, Session

from orm.engine import get_engine
from orm.models import Question
from enums import OrderDirection, DifficultyLevel
from constants import DEFAULT_SUBDOMAINS


def list_questions(order_by: str = Question.created_at.name, order_direction: OrderDirection = OrderDirection.DESC, limit: int = 20, offset: int = 0, subdomain: str = None, difficulty_level: DifficultyLevel = None):
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
    else:
        statement = statement.where(Question.subdomain.in_(DEFAULT_SUBDOMAINS))
    if difficulty_level:
        statement = statement.where(Question.level == difficulty_level)
    with Session(engine) as session:
        result = session.scalars(statement)
        questions = result.all()
    return questions
