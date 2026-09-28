from job_agent.sources.alljobs import AllJobsSource
from job_agent.sources.drushim import DrushimSource
from job_agent.sources.jobmaster import JobMasterSource
from job_agent.sources.linkedin import LinkedInSource

ALL_SOURCES = [
    LinkedInSource(),
    DrushimSource(),
    AllJobsSource(),
    JobMasterSource(),
]
