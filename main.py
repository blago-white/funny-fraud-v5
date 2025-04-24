import time
import dotenv

dotenv.load_dotenv()

from parser.parser import OfferInitializerParser

from parser.profiles.drivers import WebDriversService

from parser.sms.helper import HelperSMSService


sms_service = HelperSMSService(apikey="OXsOOoh2EMPSf5kWwwrT")

o = OfferInitializerParser(payments_card=None, driver=(WebDriversService().get_desctop(worker_id=111))[-1])

number_id, number = sms_service.get_number()

o.register(
    url="https://finuslugi.ru/podbor_zajma?utm_source=leadssu&utm_medium=affiliate&utm_campaign=pr:kredity&utm_term=53f3ff45afb1a75efefb7017ab3d2638&offer_id=11437&utm_content=125100",
    phone=number
)

START, code = time.time(), None

while True:
    while time.time() - START < 60*2:
        code = sms_service.check_code(phone_id=number_id)

        if code:
            break
    else:
        continue
    break

o.enter_registration_otp(otp=code)

START, code = time.time(), None

while True:
    while time.time() - START < 60*2:
        code = sms_service.check_code(phone_id=number_id)

        if code:
            break
    else:
        continue
    break

o.enter_approval_otp(otp=code)

try:
    o.enter_owner_passport_data()
except:
    print("PASSPORD BAD")
    raise ValueError

o.enter_owner_funds_status()

print("CONTINUE")

time.sleep(245)
