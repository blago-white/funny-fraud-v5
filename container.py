from aiogram import Bot


class BotInstanceContainer:
    _instance = None
    _bot = None

    def __init__(self, bot: Bot = None):
        if not self._instance:
            self._bot = bot

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(BotInstanceContainer, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    @property
    def bot(self):
        return self._bot
