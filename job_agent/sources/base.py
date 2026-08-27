from abc import ABC, abstractmethod
from typing import List

from job_agent.models import Vacancy


class JobSource(ABC):
    """Common interface for a job board source.

    To add a new source: subclass this, implement `fetch`, and register the
    instance in `job_agent/sources/__init__.py::ALL_SOURCES`.
    """

    name: str = "unknown"

    @abstractmethod
    def fetch(self, query: str) -> List[Vacancy]:
        """Returns vacancies matching `query`. Should not raise on network
        errors — log and return an empty list instead, so one broken source
        doesn't stop the whole daily run."""
        raise NotImplementedError
