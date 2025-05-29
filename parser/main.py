import threading
import time

from db.leads import LeadGenerationResultsService, LeadGenResultStatus, \
    LeadGenResult
from parser.sms.helper import HelperSMSService
from db.proxy import ProxyRepository

from .utils import exceptions
from .profiles.drivers import WebDriversService
from .parser.parser import OfferInitializerParser
from .parser import exceptions as parser_exceptions
from .transfer import LeadsGenerationSession
from .sms.middleware.throttling import SmsServiceThrottlingMiddleware
from .utils.generator import session_results_commiter


class LeadsGenerator:
    default_parser_class: OfferInitializerParser = OfferInitializerParser
    default_leads_db: LeadGenerationResultsService = LeadGenerationResultsService
    default_sms_service: HelperSMSService = HelperSMSService
    default_drivers_service: WebDriversService = WebDriversService

    _PHONE_ATTEMPTS_COUNT = 3

    def __init__(
            self, parser_class: OfferInitializerParser = None,
            db_service: LeadGenerationResultsService = None,
            sms_service: HelperSMSService = None,
            drivers_service: WebDriversService = None,
            proxy_service: ProxyRepository = None
    ):
        self._parser_class = parser_class or self.default_parser_class
        self._db_service = db_service or self.default_leads_db()
        self._proxy_service = proxy_service or ProxyRepository()
        self._sms_service = sms_service or self.default_sms_service()
        self._drivers_service = drivers_service or self.default_drivers_service

    def mass_generate(self, data: LeadsGenerationSession):
        print(self._sms_service, "SMS SERVICE")

        new_session_id = self._db_service.get_count()

        self._db_service.init(session_id=new_session_id)

        threads = []

        SmsServiceThrottlingMiddleware.clean_buffer()

        for ref_link in data.ref_links:
            threads.extend([threading.Thread(
                target=self.generate,
                kwargs=dict(
                    session_id=new_session_id,
                    session=LeadsGenerationSession(
                        ref_link=ref_link,
                        count=1,
                    )),
            ) for _ in range(data.count)])

        for t in threads:
            t.start()

        return new_session_id

    @session_results_commiter
    def generate(
            self, session_id: int,
            lead_id: int,
            parser: OfferInitializerParser,
            session: LeadsGenerationSession):
        number_id: str = None
        stopping_exception: Exception = None

        for _ in range(self._PHONE_ATTEMPTS_COUNT):
            if number_id:
                self._sms_service.cancel(phone_id=number_id)

            number_id, number = self._sms_service.get_number()

            try:
                parser.register(url=session.ref_link, phone=number)
            except parser_exceptions.TraficBannedError as e:
                stopping_exception = e
                break
            except Exception as e:
                stopping_exception = parser_exceptions.InitializingError(
                    crude_exception=e,
                    used_phone_id=number_id,
                    used_phone_number=number
                )
                break

            try:
                sms_code = self._get_sms_code(phone_id=number_id)
            except parser_exceptions.RegistrationSMSTimeoutError:
                continue

            try:
                parser.enter_registration_otp(otp=sms_code)
            except Exception as e:
                print(e)

                stopping_exception = parser_exceptions.InitializingError(
                    crude_exception=e,
                    used_phone_id=number_id,
                    used_phone_number=number_id
                )
                break

            break
        else:
            self._sms_service.cancel(phone_id=number_id)

            raise parser_exceptions.BadSMSService("The number of attempts to register by SMS has been spent")

        if stopping_exception:
            self._sms_service.cancel(phone_id=number_id)

            raise stopping_exception

        try:
            authorization_code = self._get_sms_code(phone_id=number_id)
        except:
            raise parser_exceptions.BadSMSService("Error receiving auth sms")

        parser.enter_approval_otp(otp=authorization_code)

        try:
            parser.enter_owner_passport_data()
        except Exception as e:
            raise exceptions.PassportCredentalsNotCorrect("Passport data not correct")

        try:
            parser.enter_owner_funds_status()
        except Exception as e:
            print("FUNDS ENTERING ERROR")

            print(e)

            time.sleep(5*60)

            raise exceptions.FundsStatusEnteringFatalError()

        self._db_service.mark_success(session_id=session_id, lead_id=lead_id)

    def _get_sms_code(self, phone_id: int):
        code, start_time = None, time.time()

        previous_code = self._sms_service.check_code(phone_id=phone_id)
        code = previous_code

        while code == previous_code:
            if (time.time() - start_time) > self._sms_service.SMS_TIMEOUT:
                self._sms_service.cancel(phone_id=phone_id)

                raise parser_exceptions.RegistrationSMSTimeoutError(
                    "No receive sms"
                )

            code = self._sms_service.check_code(phone_id=phone_id)

            time.sleep(1)

        extracted_code = "".join([i for i in code if i.isdigit()][:4])

        print(f"CODE: {extracted_code}")

        return extracted_code

    def _check_stopped_with_phone(self, *args, phone_id: int = None, **kwargs):
        try:
            self._check_stopped(*args, **kwargs)
        except SystemExit as e:
            self._sms_service.cancel(phone_id=phone_id)
            raise e

    def _check_stopped(self, session_id: int, lead_id: int):
        if self._db_service.get(
                session_id=session_id, lead_id=lead_id
        )[0].status == LeadGenResultStatus.FAILED:
            raise SystemExit(0)
