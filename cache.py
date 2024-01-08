import redis

from constants import REDIS_HOST, REDIS_PORT


_engine = None


def get_engine(echo=False):
    global _engine
    if _engine is None:
        _engine = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    return _engine


def set_string(key, value, expire: int = None):
    engine = get_engine()
    engine.set(key, value)
    if expire is not None:
        engine.expire(key, expire)


def get_string(key):
    engine = get_engine()
    return engine.get(key)
