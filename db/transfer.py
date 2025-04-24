from dataclasses import dataclass


@dataclass
class LeadGenResultStatus:
    FAILED = "f"
    SUCCESS = "s"
    PROGRESS = "r"


STATUS_MAPPING = {
    "r": LeadGenResultStatus.PROGRESS,
    "f": LeadGenResultStatus.FAILED,
    "s": LeadGenResultStatus.SUCCESS,
}


@dataclass
class LeadGenResult:
    session_id: int
    status: str = None
    error: str | None = None
    proxy: str | None = None
    ref_link: str | None = None

    lead_id: int | None = None

    def __post_init__(self):
        self.status = STATUS_MAPPING.get(self.status, "f")


@dataclass
class DayStatisticsRow:
    link: str
    count: int
