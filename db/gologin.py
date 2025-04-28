from .base import DefaultApikeyRedisRepository


class GologinApikeysRepository(DefaultApikeyRedisRepository):
    _APIKEY_KEY = "gologin:apikey"

    def get_current(self):
        return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2ODBmOTA2MTU5OTkyYzJhODQyM2QwYjMiLCJ0eXBlIjoiZGV2Iiwiand0aWQiOiI2ODBmOTA2OTljNDA0OWExNjg5NzkyMmYifQ.g9YuExpFDof3salgPGbVdCFI0p9yIFlh5XdxLiSFUNA"

    def exists(self):
        return True
