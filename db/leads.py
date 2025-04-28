import random
import time

from .base import DefaulConcurrentRepository
from .transfer import LeadGenResult, LeadGenResultStatus, STATUS_MAPPING


class LeadGenerationResultsService(DefaulConcurrentRepository):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(LeadGenerationResultsService, cls).__new__(
                cls
            )
        return cls.instance

    def get_count(self) -> int:
        try:
            return int(self._conn.get("sessions:count"))
        except:
            self._init_sessions_counter()
            return self.get_count()

    def increase_count(self):
        pipe = self._conn.pipeline()

        current = self.get_count()
        current += 1

        pipe.set(name="sessions:count", value=current)
        pipe.execute()

    @DefaulConcurrentRepository.locked(only_session_id=True)
    def init(self, session_id: int):
        if self._conn.get(f"sessions:session#{session_id}"):
            return

        self._conn.append(f"sessions:session#{session_id}",
                          "")

        self.increase_count()

        return True

    def get(self, session_id: int, lead_id: int = None) -> list[LeadGenResult]:
        try:
            leads = self._conn.get(f"sessions:session#{session_id}").decode(
                "utf-8"
            )

            assert bool(leads) is True, ValueError
        except:
            return []

        leads = [i for i in leads.split("&") if i]

        try:
            session_leads = [LeadGenResult(
                session_id=session_id,
                lead_id=int(l.split("@")[0]),
                status=STATUS_MAPPING.get(l.split("@")[1],
                                          LeadGenResultStatus.FAILED),
                error=l.split("@")[2],
                ref_link=l.split("@")[3],
                proxy=l.split("@")[4]
            ) for l in leads]
        except:
            print("LEADS", leads)

            return []

        return [l for l in session_leads
                if not lead_id or l.lead_id == lead_id]

    @DefaulConcurrentRepository.locked(only_session_id=True,
                                       only_one_thread=True)
    def add(self, session_id: int, result: LeadGenResult):
        id_ = f"sessions:session#{session_id}"

        try:
            exists = self._conn.get(id_).decode("utf-8")
        except:
            self.init(session_id=session_id)
            exists = self._conn.get(id_).decode("utf-8")

        if not exists:
            self._conn.set(name=id_,
                           value=f"0@"
                                 f"{result.status}@"
                                 f"{result.error}@"
                                 f"{result.ref_link}@"
                                 f"{result.proxy or 'localhost'}&"
                           )

            return id_, 0

        exists = [i for i in exists.split("&") if len(i) > 2]

        self._conn.set(name=id_,
                       value="&".join(exists + [
                           f"{len(exists)}@"
                           f"{result.status}@"
                           f"{result.error}@"
                           f"{result.ref_link}@"
                           f"{result.proxy or 'localhost'}"
                       ])
                       )

        return id_, len(exists)

    @DefaulConcurrentRepository.locked()
    def mark_success(self, session_id: int, lead_id: int):
        return self._change_status(
            status=LeadGenResultStatus.SUCCESS,
            session_id=session_id,
            lead_id=lead_id
        )

    @DefaulConcurrentRepository.locked()
    def mark_failed(
            self, session_id: int, lead_id: int,
            error: str = None):
        return self._change_status(
            status=LeadGenResultStatus.FAILED,
            session_id=session_id,
            lead_id=lead_id,
            error=error
        )

    @DefaulConcurrentRepository.locked()
    def change_status(
            self, session_id: int,
            lead_id: int,
            status: str,
            error: str = None):
        return self._change_status(session_id=session_id,
                                   lead_id=lead_id,
                                   status=status,
                                   error=error)

    @DefaulConcurrentRepository.locked(only_session_id=True)
    def drop_session(self, session_id: int):
        results = []

        for unsuccess_lead in list(filter(
            lambda l: l.status != LeadGenResultStatus.SUCCESS,
            self.get(session_id=session_id)
        )):
            results.append(self._change_status(
                session_id=session_id,
                lead_id=unsuccess_lead.lead_id,
                status=LeadGenResultStatus.FAILED
            ))

        return all(results)

    def _change_status(
            self, session_id: int,
            lead_id: int,
            status: str,
            error: str = None):
        session = self.get(session_id=session_id)

        if not session:
            return False

        id_ = f"sessions:session#{session_id}"

        exists = self._conn.get(id_).decode("utf-8").split("&")

        try:
            result = self.get(session_id=session_id, lead_id=lead_id)[0]
        except:
            return

        for i_id, i in enumerate(exists):
            lead_id_raw = i.split("@")[0]

            if lead_id_raw.isdigit() and int(lead_id_raw) == int(lead_id):
                exists[i_id] = (f"{lead_id}@{status}@"
                                f"{error or result.error}@"
                                f"{result.ref_link}@"
                                f"{result.proxy}")
                break

        self._conn.set(name=id_,
                       value="&".join(exists))

        return session_id

    def _init_sessions_counter(self):
        self._conn.append("sessions:count", 0)
