from .base import DefaultApikeyRedisRepository


class GologinApikeysRepository(DefaultApikeyRedisRepository):
    _APIKEY_KEY = "gologin:apikey"

    def get_current(self):
        return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2ODA0Yzk2MTdiNGNjZTE2YjYyY2EzMmMiLCJ0eXBlIjoiZGV2Iiwiand0aWQiOiI2ODA3NTVjZmY5MGIxMjAzYjVmZDA5ZDQifQ.I_trgvUlnuZwRZHR3IWmqw7Tj9KOcvpQxuIybtKcoas"

    def exists(self):
        return True
