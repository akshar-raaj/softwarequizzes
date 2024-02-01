"""
Deal with SQLAlchemy engine.

SQLAlchemy engine manages connectivity with the database and provides mechanism to execute queries.
"""
from sqlalchemy import create_engine

from constants import DATABASE_CONNECTION_STRING, DATABASE_REPLICA_CONNECTION_STRING


_engine = None
_replica_engine = None


def get_engine(echo=False, replica=False):
    global _engine
    global _replica_engine
    if replica is True:
        if _replica_engine is not None:
            return _replica_engine
        _replica_engine = create_engine(DATABASE_REPLICA_CONNECTION_STRING, echo=echo)
        return _replica_engine
    else:
        if _engine is not None:
            return _engine
        _engine = create_engine(DATABASE_CONNECTION_STRING, echo=echo)
        return _engine


def migrate(force=False):
    from orm.models import Base
    engine = get_engine()
    if force:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
