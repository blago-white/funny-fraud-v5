from ..sms365 import SMS365Service
from ..helpersms import HelperSMSService

from db.sms import (Sms365ServiceApikeyRepository,
                    HelperSmsServiceApikeyRepository)


class SMS365:
    KEY = "H"


class HELPERSMS:
    KEY = "S"


SMS_SERVICES_MAPPER = {
    SMS365.KEY: SMS365Service,
    HELPERSMS.KEY: HelperSMSService
}

SMS_DB_REPOSITORY_MAPPER = {
    HELPERSMS.KEY: HelperSmsServiceApikeyRepository(),
    SMS365.KEY: Sms365ServiceApikeyRepository()
}
