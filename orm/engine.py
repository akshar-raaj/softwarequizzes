from sqlalchemy import create_engine

from constants import DATABASE_CONNECTION_STRING


_engine = None


def get_engine(echo=False):
    global _engine
    if _engine is None:
        _engine = create_engine(DATABASE_CONNECTION_STRING, echo=echo)
    return _engine


def migrate(force=False):
    from orm.models import Base
    engine = get_engine()
    if force:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
