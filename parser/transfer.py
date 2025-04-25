from dataclasses import dataclass


@dataclass
class LeadsGenerationSession:
    count: int = 1
    ref_links: list[str] = None
    ref_link: str = None
