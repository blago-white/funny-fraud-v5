import time
import dotenv

dotenv.load_dotenv()

from parser.parser.parser import OfferInitializerParser

from profiles.drivers import WebDriversService


o = OfferInitializerParser(payments_card=None, driver=WebDriversService().get_desctop(worker_id=111))

o.register(
    url="https://finuslugi.ru/podbor_zajma?utm_source=leadssu&utm_medium=affiliate&utm_campaign=pr:kredity&utm_term=53f3ff45afb1a75efefb7017ab3d2638&offer_id=11437&utm_content=125100",
    phone="79952481751"
)

time.sleep(245)
