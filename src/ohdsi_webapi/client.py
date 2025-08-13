from __future__ import annotations

from .auth import AuthStrategy
from .cache import cache_stats, clear_cache
from .http import HttpExecutor
from .services.cohorts import CohortService
from .services.concept_sets import ConceptSetService
from .services.info import InfoService
from .services.jobs import JobsService
from .services.sources import SourcesService
from .services.vocabulary import VocabularyService


class WebApiClient:
    def __init__(self, base_url: str, *, auth: AuthStrategy | None = None, timeout: float = 30.0, verify: bool | str = True):
        self._http = HttpExecutor(
            base_url.rstrip("/"), timeout=timeout, auth_headers_cb=(auth.auth_headers if auth else None), verify=verify
        )

        # Core service objects (primary interface)
        self.info = InfoService(self._http)
        self.sources = SourcesService(self._http)
        self.vocabulary = VocabularyService(self._http)
        self.vocab = self.vocabulary  # Alias for convenience
        self.concept_sets = ConceptSetService(self._http)
        self.cohorts = CohortService(self._http)
        self.jobs = JobsService(self._http)

        # Explicit REST-style convenience methods
        # Concept set methods
        self.conceptset_expression = self.concept_sets.expression
        self.conceptset_items = self.concept_sets.resolve
        self.conceptset_export = self.concept_sets.export
        self.conceptset_generationinfo = self.concept_sets.generation_info

        # Cohort definition methods
        self.cohortdefinition_generate = self.cohorts.generate
        self.cohortdefinition_info = self.cohorts.generation_status
        self.cohortdefinition_inclusionrules = self.cohorts.inclusion_rules

        # Job methods
        self.job_status = self.jobs.status

    def close(self):
        self._http.close()

    def __enter__(self):  # pragma: no cover
        return self

    def __exit__(self, exc_type, exc, tb):  # pragma: no cover
        self.close()

    # Cache management methods
    def clear_cache(self) -> None:
        """Clear all cached data."""
        clear_cache()

    def cache_stats(self) -> dict:
        """Get cache statistics."""
        return cache_stats()
