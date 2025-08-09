from __future__ import annotations

from typing import Any, Iterable

from ..cache import cached_method
from ..http import HttpExecutor
from ..models.vocabulary import Concept


class VocabularyService:
    """Service for accessing OMOP vocabulary and concept operations.

    This service provides comprehensive access to the OMOP Common Data Model
    vocabulary, including concept search, retrieval, and relationship traversal.
    Results are cached for performance optimization.
    """

    def __init__(self, http: HttpExecutor):
        self._http = http

    def _normalize_concept_payload(self, data: dict[str, Any]) -> dict[str, Any]:
        # WebAPI may return uppercase keys (Atlas style). Map to snake/camel expected by model.
        mapping = {
            "CONCEPT_ID": "conceptId",
            "CONCEPT_NAME": "conceptName",
            "VOCABULARY_ID": "vocabularyId",
            "CONCEPT_CODE": "conceptCode",
            "CONCEPT_CLASS_ID": "conceptClassId",
            "STANDARD_CONCEPT": "standardConcept",
            "DOMAIN_ID": "domainId",
            "VALID_START_DATE": "validStartDate",
            "VALID_END_DATE": "validEndDate",
            "INVALID_REASON": "invalidReason",
        }
        normalized: dict[str, Any] = {}
        for k, v in data.items():
            nk = mapping.get(k, k)
            # Convert timestamp dates to strings if needed
            if nk in ("validStartDate", "validEndDate") and isinstance(v, int):
                # Convert millisecond timestamp to ISO date string
                from datetime import datetime

                v = datetime.fromtimestamp(v / 1000).strftime("%Y-%m-%d")
            normalized[nk] = v
        return normalized

    def _concept_from_any(self, obj: Any) -> Concept:
        if not isinstance(obj, dict):
            raise ValueError("Unexpected concept data")
        # Always normalize to handle both uppercase keys and timestamp dates
        obj = self._normalize_concept_payload(obj)
        return Concept(**obj)  # type: ignore[arg-type]

    @cached_method(ttl_seconds=3600)  # 1 hour for individual concepts (relatively stable)
    def get_concept(self, concept_id: int, *, force_refresh: bool = False) -> Concept:
        """Fetch a single concept by ID.

        Parameters
        ----------
        concept_id : int
            The OMOP concept ID to retrieve.
        force_refresh : bool, default False
            If True, bypass cache and fetch fresh data from the server.

        Returns
        -------
        Concept
            Complete concept information including name, vocabulary, domain, etc.

        Examples
        --------
        >>> # Get a specific concept
        >>> concept = client.vocabulary.get_concept(201826)
        >>> print(f"{concept.concept_name} ({concept.vocabularyId})")
        'Type 2 diabetes mellitus (SNOMED)'
        >>>
        >>> # Force refresh from server
        >>> fresh_concept = client.vocabulary.get_concept(201826, force_refresh=True)

        Notes
        -----
        Results are cached for 1 hour by default to improve performance.
        Use force_refresh=True if you need the most current data.
        """
        data = self._http.get(f"/vocabulary/concept/{concept_id}")
        return self._concept_from_any(data)

    def concept(self, concept_id: int, *, force_refresh: bool = False) -> Concept:
        """Alias for get_concept() to match WebAPI endpoint path (/vocabulary/concept/{id}).

        Parameters
        ----------
        concept_id : int
            The OMOP concept ID to retrieve.
        force_refresh : bool, default False
            If True, bypass cache and fetch fresh data.

        Returns
        -------
        Concept
            Complete concept information.
        """
        return self.get_concept(concept_id, force_refresh=force_refresh)

    @cached_method(ttl_seconds=900)  # 15 minutes for search results (dynamic content)
    def search(
        self,
        query: str,
        *,
        vocabulary_id: str | None = None,
        concept_class_id: str | None = None,
        domain_id: str | None = None,
        standard_concept: str | None = None,  # 'S','C', etc.
        invalid_reason: str | None = None,  # 'D','U', etc.
        page: int = 1,
        page_size: int = 20,
        sort: str | None = None,
    ) -> list[Concept]:
        """Search for concepts by name or description.

        Parameters
        ----------
        query : str
            The search term to look for in concept names and synonyms.
        vocabulary_id : str, optional
            Filter results to specific vocabulary (e.g., 'SNOMED', 'ICD10CM').
        concept_class_id : str, optional
            Filter by concept class (e.g., 'Clinical Finding', 'Ingredient').
        domain_id : str, optional
            Filter by domain (e.g., 'Condition', 'Drug', 'Procedure').
        standard_concept : str, optional
            Filter by standard concept flag ('S' for standard, 'C' for classification).
        invalid_reason : str, optional
            Filter by validity ('D' for deleted, 'U' for updated).
        page : int, default 1
            Page number for pagination (1-based).
        page_size : int, default 20
            Number of results per page (max typically 100).
        sort : str, optional
            Sort order specification.

        Returns
        -------
        list of Concept
            List of matching concepts with full metadata.

        Examples
        --------
        >>> # Basic search
        >>> results = client.vocabulary.search("diabetes")
        >>>
        >>> # Search with filters
        >>> conditions = client.vocabulary.search(
        ...     "hypertension",
        ...     domain_id="Condition",
        ...     standard_concept="S",
        ...     page_size=10
        ... )
        """
        # Build JSON body according to WebAPI documentation
        body: dict[str, Any] = {"QUERY": query}

        # Add optional filters to JSON body
        if vocabulary_id:
            body["VOCABULARY_ID"] = [vocabulary_id] if isinstance(vocabulary_id, str) else vocabulary_id
        if concept_class_id:
            body["CONCEPT_CLASS_ID"] = [concept_class_id] if isinstance(concept_class_id, str) else concept_class_id
        if domain_id:
            body["DOMAIN_ID"] = [domain_id] if isinstance(domain_id, str) else domain_id
        if standard_concept:
            body["STANDARD_CONCEPT"] = standard_concept
        if invalid_reason:
            body["INVALID_REASON"] = invalid_reason

        # Note: WebAPI search endpoint doesn't seem to support pagination in POST body
        # We'll handle pagination at the client level if needed

        data = self._http.post("/vocabulary/search/", json_body=body)
        if isinstance(data, list):
            concepts = [self._concept_from_any(d) for d in data]
            # Client-side pagination since WebAPI doesn't support it in POST
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            return concepts[start_idx:end_idx]
        return []

    def descendants(self, concept_id: int) -> list[Concept]:
        """Get all descendant concepts of a given concept.

        Descendant concepts are those that are hierarchically "below" the given
        concept in the OMOP vocabulary relationships (e.g., specific subtypes).

        Parameters
        ----------
        concept_id : int
            The OMOP concept ID to find descendants for.

        Returns
        -------
        list of Concept
            All concepts that are descendants of the input concept.

        Examples
        --------
        >>> # Get all subtypes of diabetes
        >>> diabetes_descendants = client.vocabulary.descendants(201826)
        >>> for desc in diabetes_descendants[:5]:
        ...     print(f"  {desc.concept_id}: {desc.concept_name}")
        """
        data = self._http.get(f"/vocabulary/concept/{concept_id}/descendants")
        if isinstance(data, list):
            return [self._concept_from_any(d) for d in data]
        return []

    @cached_method(ttl_seconds=1800)  # 30 minutes for domains (fairly stable)
    def related(self, concept_id: int) -> list[Concept]:
        """Get concepts related to the given concept.

        Returns concepts that are related through various relationships
        (maps to, is a, etc.) as defined in the OMOP vocabulary.

        Parameters
        ----------
        concept_id : int
            The OMOP concept ID to find related concepts for.

        Returns
        -------
        list of Concept
            All concepts related to the input concept through vocabulary relationships.

        Examples
        --------
        >>> # Get related concepts
        >>> related = client.vocabulary.related(201826)
        >>> for rel in related[:5]:
        ...     print(f"  {rel.concept_id}: {rel.concept_name}")
        """
        data = self._http.get(f"/vocabulary/concept/{concept_id}/related")
        if isinstance(data, list):
            return [self._concept_from_any(d) for d in data]
        return []

    def bulk_get(self, concept_ids: Iterable[int]) -> list[Concept]:
        ids = list(concept_ids)
        if not ids:
            return []
        data = self._http.post("/vocabulary/concepts", json_body=ids)
        if isinstance(data, list):
            return [self._concept_from_any(d) for d in data]
        return []

    @cached_method(ttl_seconds=1800)  # 30 minutes for domains (fairly stable)
    def list_domains(self, *, force_refresh: bool = False) -> list[dict[str, Any]]:
        """Return available vocabulary domains.

        Args:
            force_refresh: If True, bypass cache and fetch fresh data

        WebAPI /vocabulary/domains may return a list of objects with uppercase keys
        like DOMAIN_ID / DOMAIN_NAME or already normalized. We normalize minimally.
        """
        data = self._http.get("/vocabulary/domains")
        out: list[dict[str, Any]] = []
        if isinstance(data, list):
            for d in data:
                if isinstance(d, dict):
                    if "DOMAIN_ID" in d and "domainId" not in d:
                        out.append(
                            {
                                "domainId": d.get("DOMAIN_ID"),
                                "domainName": d.get("DOMAIN_NAME") or d.get("DOMAIN_ID"),
                            }
                        )
                    else:
                        # Pass through existing keys but ensure domainId present
                        out.append(
                            {
                                "domainId": d.get("domainId") or d.get("DOMAIN_ID") or d.get("id"),
                                "domainName": d.get("domainName") or d.get("DOMAIN_NAME") or d.get("name") or d.get("domainId"),
                                **{k: v for k, v in d.items() if k not in {"DOMAIN_ID", "DOMAIN_NAME"}},
                            }
                        )
        return out

    def domains(self, *, force_refresh: bool = False) -> list[dict[str, Any]]:
        """Alias for list_domains() to match WebAPI endpoint naming (/vocabulary/domains)."""
        return self.list_domains(force_refresh=force_refresh)

    def lookup_identifiers(
        self,
        identifiers: Iterable[tuple[str, str] | dict[str, Any]],
        *,
        include_descendants: bool = False,
        include_mapped: bool = False,
    ) -> list[Concept]:
        """Bulk resolve source codes to concepts.

        identifiers: iterable of (code, vocabularyId) tuples OR dicts that already
        conform to the WebAPI shape {identifier, vocabularyId, includeDescendants?, includeMapped?}.
        include_descendants / include_mapped: default flags applied to tuple inputs
        (not overriding explicit dict-provided flags).
        Returns a flattened list of Concept objects (duplicates possible if multiple
        identifiers map to same concept). If the WebAPI returns per-identifier grouping,
        groups are flattened here for simplicity.
        """
        payload: list[dict[str, Any]] = []
        for item in identifiers:
            if isinstance(item, tuple):
                code, vocab = item
                payload.append(
                    {
                        "identifier": code,
                        "vocabularyId": vocab,
                        "includeDescendants": include_descendants,
                        "includeMapped": include_mapped,
                    }
                )
            elif isinstance(item, dict):
                obj = dict(item)  # shallow copy
                obj.setdefault("includeDescendants", include_descendants)
                obj.setdefault("includeMapped", include_mapped)
                # Accept alternative key names
                if "code" in obj and "identifier" not in obj:
                    obj["identifier"] = obj.pop("code")
                payload.append(obj)
            else:  # pragma: no cover - defensive
                raise TypeError("Identifiers must be tuple or dict")
        if not payload:
            return []
        data = self._http.post("/vocabulary/lookup/identifiers", json_body=payload)
        concepts: list[Concept] = []
        if isinstance(data, list):
            for entry in data:
                # Some implementations return a wrapper like {"concept": {...}} or direct concept-like dict
                if isinstance(entry, dict):
                    if "concept" in entry and isinstance(entry["concept"], dict):
                        concepts.append(self._concept_from_any(entry["concept"]))
                    else:
                        # Try direct concept
                        try:
                            concepts.append(self._concept_from_any(entry))
                        except Exception:  # pragma: no cover
                            continue
        return concepts
