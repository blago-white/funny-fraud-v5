import random
import time
from abc import ABCMeta, abstractmethod

import redis


class BaseRedisService(metaclass=ABCMeta):
    _conn: redis.Redis = redis.Redis.from_url("redis://localhost:6379/0")

    def __init__(self, conn: redis.Redis = None):
        self._conn = conn or self._conn


class DefaultApikeyRedisRepository(BaseRedisService, metaclass=ABCMeta):
    _conn: redis.Redis
    _APIKEY_KEY: str = None

    @property
    def exists(self):
        return bool(self.get_current())

    def get_current(self) -> str | None:
        return (self._conn.get(name=self._APIKEY_KEY) or b"").decode()

    def set(self, new_apikey: str):
        self._conn.set(name=self._APIKEY_KEY, value=new_apikey)

        return new_apikey


class BaseConcurrentRepository(metaclass=ABCMeta):
    _locked: str = False

    @abstractmethod
    def lock(self, *args, **kwargs):
        pass

    @abstractmethod
    def unlock(self, *args, **kwargs):
        pass

    @abstractmethod
    def wait_for_lock(self, *args, **kwargs):
        pass

    @classmethod
    @abstractmethod
    def locked(cls, *args, **kwargs):
        pass


class SimpleConcurrentRepository(BaseConcurrentRepository):
    _locked: str = False

    def lock(self):
        if self._locked:
            return False

        self._locked = True

        return True

    def unlock(self):
        self._locked = False

    def wait_for_lock(self):
        c = 0

        while c < 1500:
            if self.lock():
                return True

            time.sleep(.01)
            c += 1

    @classmethod
    def locked(cls):
        def wrapper(func):
            def wrapped(*args, **kwargs):
                self: SimpleConcurrentRepository = args[0]

                if not issubclass(type(self), cls):
                    raise TypeError("Not correct decorator place")

                self.wait_for_lock()

                result = func(*args, **kwargs)

                self.unlock()

                return result

            return wrapped

        return wrapper
