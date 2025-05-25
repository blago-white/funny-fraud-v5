import time
from typing import TYPE_CHECKING

from parser.transfer import LeadsGenerationSession
from requests.exceptions import JSONDecodeError

from db.credentials import CredentalsListEndedError
from db.credentials import OwnerCredentialsTxtRepository
from db.transfer import LeadGenResultStatus, LeadGenResult
from parser.parser import exceptions
from parser.parser.parser import OfferInitializerParser

if TYPE_CHECKING:
    from parser.main import LeadsGenerator
else:
    LeadsGenerator = object


def session_results_commiter(func):
    def _close_driver(drivers_service, pid, initializer):
        try:
            drivers_service.gologin_manager.delete_profile(pid=pid)
            initializer.driver.close()
            return True
        except:
            return False

    def convert_ref_link(ref_link):
        if "utm_content" in ref_link:
            return ref_link.split('&utm_content=')[-1].split("&")[0]
        elif "aff_id" in ref_link:
            return ref_link.split('?aff_id=')[-1].split("&")[0]
        else:
            return ref_link

    def wrapped(*args,
                lead_id: int = None,
                _retry_number=0,
                **kwargs):
        if len(args) > 1:
            raise ValueError("Only kwargs")

        self: LeadsGenerator = args[0]

        session_id, session = (
            kwargs.get("session_id"), kwargs.get("session")
        )

        print("KWRGS", kwargs, kwargs.get("session"))

        session: LeadsGenerationSession

        if lead_id is None:
            _, lead_id = self._db_service.add(
                session_id=session_id,
                result=LeadGenResult(
                    session_id=session_id,
                    status=LeadGenResultStatus.PROGRESS,
                    ref_link=convert_ref_link(session.ref_link),
                    error="",
                )
            )

        print(f"LEAD #{lead_id} STARTED")

        for _ in range(10):
            time.sleep(lead_id*0.25)

            proxy = self._proxy_service.next()

            try:
                pid, driver = self._drivers_service().get_desctop(
                    proxy=proxy,
                    worker_id=lead_id + 1
                )
                break
            except JSONDecodeError as e:
                print(f"LEAD #{lead_id} GOLOGIN RESPONSE FAILED - {e} | {repr(e)}")

                return self._db_service.mark_failed(
                    session_id=session_id,
                    lead_id=lead_id,
                    error=f"GOLOGIN RESPONSE FAILED: \n\n{repr(e)}\n\n{e}"
                )
            except Exception as e:
                print(f"LEAD #{lead_id} FAILED - {e} {repr(e)}")
        else:
            print(f"LEAD #{lead_id} CANT RUN GOLOGIN")
            return self._db_service.mark_failed(
                session_id=session_id,
                lead_id=lead_id,
                error=f"CANT RUN GOLOGIN AFTER 15 RETRY"
            )

        owner_credentals = OwnerCredentialsTxtRepository().get_next()

        try:
            parser: OfferInitializerParser = self._parser_class(
                driver=driver,
                owner_data_generator=owner_credentals
            )
        except CredentalsListEndedError:
            return self._db_service.mark_failed(
                session_id=session_id,
                lead_id=lead_id,
                error="Password data list end, update!"
            )
        except Exception as e:
            return self._db_service.mark_failed(
                session_id=session_id,
                lead_id=lead_id,
                error=f"Parser initialization error: {str(e)}"
            )

        print(f"LEAD #{lead_id} BROWSER INITED")

        kwargs |= {"lead_id": lead_id,
                   "parser": parser,
                   "session": LeadsGenerationSession(
                       ref_link=session.ref_link,
                   )}

        try:
            func(*args, **kwargs)
        except (exceptions.TraficBannedError, exceptions.InitializingError) as e:
            print("ERROR INITIALIZING : ", e)

            # OwnerCredentialsXLSRepository().restore_unused(credentals=owner_credentals)

            _close_driver(drivers_service=self._drivers_service(), pid=pid, initializer=parser)

            try:
                return wrapped(
                    *args,
                    lead_id=lead_id,
                    _retry_number=_retry_number+1,
                    **kwargs
                )
            except:
                _close_driver(drivers_service=self._drivers_service(), pid=pid, initializer=parser)

                if _retry_number >= 3:
                    self._db_service.mark_failed(
                        session_id=session_id,
                        lead_id=lead_id,
                        error=f"Parser initialization error: {str(e)}"
                    )
                    raise e

                return wrapped(
                    *args,
                    _retry_number=_retry_number+1,
                    **kwargs
                )
        except Exception as e:
            print(f"LEAD #{lead_id} FATAL ERROR : {e}")

            _close_driver(drivers_service=self._drivers_service(), pid=pid, initializer=parser)

            self._db_service.mark_failed(
                session_id=session_id,
                lead_id=lead_id,
                error=f"Parser initialization error: {str(e)}"
            )

            if _retry_number >= 3:
                self._db_service.mark_failed(
                    session_id=session_id,
                    lead_id=lead_id,
                    error=f"Parser initialization error: {str(e)}"
                )
                raise e

            return wrapped(
                *args,
                _retry_number=_retry_number+1,
                **kwargs
            )

    return wrapped
