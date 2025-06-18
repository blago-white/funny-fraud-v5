from enum import Enum

from .base import BaseRedisService
from .base import DefaultApikeyRedisRepository


class HelperSmsServiceApikeyRepository(DefaultApikeyRedisRepository):
    _APIKEY_KEY = "sms:helper-sms-apikey"


class Sms365ServiceApikeyRepository(DefaultApikeyRedisRepository):
    _APIKEY_KEY = "sms:sms-365-apikey"
