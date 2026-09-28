from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Vacancy:
    title: str
    company: str
    location: str
    url: str
    description: str = ""
    published_at: Optional[str] = None  # ISO date string if known
    source: str = ""
    matched_query: str = ""
    score: float = field(default=0.0)
    why_matches: str = ""
    # Site-specific job id, for boards whose job URLs live in the query
    # string (e.g. AllJobs ?JobID=...), where the URL key would collide.
    external_id: str = ""

    @property
    def dedup_key(self) -> str:
        if self.external_id:
            return f"{self.source.lower()}:{self.external_id}"
        # The URL (minus tracking query params) is stable enough to key on.
        return self.url.split("?")[0].rstrip("/").lower()
