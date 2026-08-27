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

    @property
    def dedup_key(self) -> str:
        # The URL (minus tracking query params) is stable enough to key on.
        return self.url.split("?")[0].rstrip("/").lower()
