from .profiles.drivers import WebDriversService
from .parser.parser import OfferInitializerParser


class LeadsGenerator:
    default_parser_class: OfferInitializerParser = OfferInitializerParser

    def __init__(
            self, parser_class: OfferInitializerParser = None,
            db_service: LeadGenerationResultsService = None,
            sms_service: ElSmsSMSCodesService = None,
            drivers_service: WebDriversService = None,
            proxy_service: ProxyRepository = None
    ):
        self._parser_class = parser_class or self.default_parser_class
        self._db_service = db_service or LeadGenerationResultsService()
        self._proxy_service = proxy_service or ProxyRepository()
        self._sms_service = sms_service or ElSmsSMSCodesService()
        self._drivers_service = drivers_service or WebDriversService()
