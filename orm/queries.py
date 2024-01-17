from sqlalchemy import select
from sqlalchemy.orm import selectinload, Session

from orm.engine import get_engine
from orm.models import Question, User

from enums import OrderDirection, DifficultyLevel
from constants import DEFAULT_SUBDOMAINS


def list_questions(order_by: str = Question.id.name, order_direction: OrderDirection = OrderDirection.DESC, limit: int = 20, offset: int = 0, subdomain: str = None, difficulty_level: DifficultyLevel = None, all_subdomains=False):
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
    if all_subdomains is False:
        if subdomain:
            statement = statement.where(Question.subdomain == subdomain)
        else:
            statement = statement.where(Question.subdomain.in_(DEFAULT_SUBDOMAINS))
    else:
        # Do not apply filter on subdomains
        pass
    if difficulty_level:
        statement = statement.where(Question.level == difficulty_level)
    with Session(engine) as session:
        result = session.scalars(statement)
        questions = result.all()
    return questions


def read_user(email: str = None, pk: int = None) -> User:
    engine = get_engine()
    if email is not None:
        statement = select(User).where(User.email == email)
    if pk is not None:
        statement = select(User).where(User.id == pk)
    with Session(engine) as session:
        user = session.scalars(statement).first()
    return user
