from dataclasses import dataclass

from aiogram.types import Message

from parser.sms.base import BaseSmsService
from parser.sms.middleware.stats import SmsRequestsStatMiddleware


@dataclass
class SessionStatusPullingCallStack:
    session_id: int
    sms_service: BaseSmsService
    initiator_message: Message
    default_sms_service_balance: float = None
    session_timeout: int = 60 * 60
    supervisor_label: str = ""
    stats_middleware: SmsRequestsStatMiddleware = SmsRequestsStatMiddleware()
