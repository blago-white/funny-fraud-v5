from functools import wraps

from db.gologin import GologinApikeysRepository
from db.leads import LeadGenerationResultsService
from db.proxy import ProxyRepository
from db.sms import HelperSmsServiceApikeyRepository
from db.statistics import LeadsGenerationStatisticsService
from parser.main import LeadsGenerator


def db_services_provider(
        provide_leads: bool = True,
        provide_gologin: bool = True,
        provide_helper: bool = False,
        provide_proxy: bool = False,
        provide_stats: bool = False):
    def wrapper(func):
        @wraps(func)
        async def wrapped(*args, **kwargs):
            db_services = {}

            if provide_leads:
                db_services.update(leadsdb=LeadGenerationResultsService())

            if provide_gologin:
                db_services.update(gologindb=GologinApikeysRepository())

            if provide_helper:
                db_services.update(helperdb=HelperSmsServiceApikeyRepository())

            if provide_proxy:
                db_services.update(proxydb=ProxyRepository())

            if provide_stats:
                db_services.update(statsdb=LeadsGenerationStatisticsService())

            return await func(*args, **kwargs, **db_services)

        return wrapped

    return wrapper


def leads_service_provider(func):
    @wraps(func)
    async def wrapped(*args, **kwargs):
        return await func(*args, **kwargs, parser_service_class=LeadsGenerator)

    return wrapped
