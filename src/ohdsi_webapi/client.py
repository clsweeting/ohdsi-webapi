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
        self.info = InfoService(self._http)
        self.sources = SourcesService(self._http)
        self.vocabulary = VocabularyService(self._http)  # Naming consistent with WebAPI path (/vocabulary/)
        self.vocab = self.vocabulary  # Alias for convenience
        self.concept_sets = ConceptSetService(self._http)
        self.conceptset = self.concept_sets  # Alias for WebAPI path consistency (/conceptset/)
        self.cohorts = CohortService(self._http)
        self.cohortdefinition = self.cohorts  # Alias for WebAPI path consistency (/cohortdefinition/)
        self.jobs = JobsService(self._http)

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
