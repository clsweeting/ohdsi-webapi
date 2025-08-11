from __future__ import annotations

from typing import Any

from .auth import AuthStrategy
from .cache import cache_stats, clear_cache
from .http import HttpExecutor
from .services.cohorts import CohortService
from .services.concept_sets import ConceptSetService
from .services.info import InfoService
from .services.jobs import JobsService
from .services.sources import SourcesService
from .services.vocabulary import VocabularyService


class PredictableServiceWrapper:
    """Wrapper that makes a service callable to match REST endpoint patterns."""

    def __init__(self, service: Any):
        self._service = service

    def __call__(self, resource_id: int | None = None, *args, **kwargs):
        """Handle calls like conceptset() and conceptset(123)."""
        if resource_id is None:
            # GET /conceptset/ -> list()
            return self._service.list(*args, **kwargs)
        else:
            # GET /conceptset/{id} -> get(id)
            return self._service.get(resource_id, *args, **kwargs)

    def __getattr__(self, name: str):
        """Delegate all other attribute access to the wrapped service."""
        return getattr(self._service, name)


class PredictableInfoWrapper:
    """Wrapper that makes info service callable as info()."""

    def __init__(self, service: Any):
        self._service = service

    def __call__(self, *args, **kwargs):
        """Handle calls like info()."""
        return self._service.get(*args, **kwargs)

    def __getattr__(self, name: str):
        """Delegate all other attribute access to the wrapped service."""
        return getattr(self._service, name)


class WebApiClient:
    def __init__(self, base_url: str, *, auth: AuthStrategy | None = None, timeout: float = 30.0, verify: bool | str = True):
        self._http = HttpExecutor(
            base_url.rstrip("/"), timeout=timeout, auth_headers_cb=(auth.auth_headers if auth else None), verify=verify
        )
        self._info_service = InfoService(self._http)
        self.info = PredictableInfoWrapper(self._info_service)  # Callable for REST pattern
        self.sources = SourcesService(self._http)
        self.vocabulary = VocabularyService(self._http)  # Naming consistent with WebAPI path (/vocabulary/)
        self.vocab = self.vocabulary  # Alias for convenience
        self.concept_sets = ConceptSetService(self._http)
        self.conceptset = PredictableServiceWrapper(self.concept_sets)  # Callable for REST pattern
        self.cohorts = CohortService(self._http)
        self.cohortdefinition = PredictableServiceWrapper(self.cohorts)  # Callable for REST pattern
        self._jobs_service = JobsService(self._http)
        self.jobs = self._jobs_service  # Backwards compatibility

    def __getattr__(self, name: str) -> Any:
        """Handle predictable method calls that mirror REST endpoints.

        This enables calls like:
        - client.conceptset_expression(123) -> GET /conceptset/123/expression
        - client.cohortdefinition_generate(123, source) -> POST /cohortdefinition/123/generate/source
        - client.source_sources() -> GET /source/sources
        - client.job(execution_id) -> GET /job/{execution_id}
        """
        # Handle conceptset_* predictable methods
        if name.startswith("conceptset_"):
            sub_resource = name[11:]  # Remove "conceptset_" prefix
            return self._create_conceptset_sub_method(sub_resource)

        # Handle cohortdefinition_* predictable methods
        elif name.startswith("cohortdefinition_"):
            sub_resource = name[17:]  # Remove "cohortdefinition_" prefix
            return self._create_cohortdefinition_sub_method(sub_resource)

        # Handle source_sources() -> GET /source/sources
        elif name == "source_sources":
            return lambda: self.sources.list()

        # Handle job(execution_id) -> GET /job/{execution_id}
        elif name == "job":
            return lambda execution_id: self._jobs_service.status(execution_id)

        # If not a predictable method, raise AttributeError
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def _create_conceptset_sub_method(self, sub_resource: str):
        """Create methods for conceptset sub-resources like conceptset_expression(id)."""
        if sub_resource == "expression":
            return lambda concept_set_id: self.concept_sets.expression(concept_set_id)
        elif sub_resource == "items":
            return lambda concept_set_id: self.concept_sets.resolve(concept_set_id)
        elif sub_resource == "export":
            return lambda concept_set_id, format="csv": self.concept_sets.export(concept_set_id, format)
        elif sub_resource == "generationinfo":
            return lambda concept_set_id: self.concept_sets.generation_info(concept_set_id)
        else:
            raise AttributeError(f"Unknown conceptset sub-resource: {sub_resource}")

    def _create_cohortdefinition_sub_method(self, sub_resource: str):
        """Create methods for cohortdefinition sub-resources like cohortdefinition_generate(id, source)."""
        if sub_resource == "generate":
            return lambda cohort_id, source_key: self.cohorts.generate(cohort_id, source_key)
        elif sub_resource == "info":
            return lambda cohort_id, source_key=None: (
                self.cohorts.generation_status(cohort_id, source_key) if source_key else self.cohorts.get(cohort_id)
            )
        elif sub_resource == "inclusionrules":
            return lambda cohort_id, source_key: self.cohorts.inclusion_rules(cohort_id, source_key)
        else:
            raise AttributeError(f"Unknown cohortdefinition sub-resource: {sub_resource}")

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
