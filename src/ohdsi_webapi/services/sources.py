from __future__ import annotations
from typing import Iterable
from ..http import HttpExecutor
from ..models.source import Source

class SourcesService:
    """Service for managing OHDSI data sources.
    
    This service provides access to available data sources (CDM databases)
    configured in the WebAPI instance. Data sources are used for cohort
    generation, analysis, and vocabulary operations.
    """
    
    def __init__(self, http: HttpExecutor):
        self._http = http

    def list(self) -> list[Source]:
        """List all available data sources.
        
        Returns
        -------
        list of Source
            List of available data source configurations, each containing
            source key, name, dialect, and connection information.
            
        Examples
        --------
        >>> client = WebApiClient(base_url="http://localhost:8080/WebAPI")
        >>> sources = client.sources.list()
        >>> for source in sources:
        ...     print(f"{source.sourceName} ({source.sourceKey})")
        """
        data = self._http.get("/source/sources")
        if isinstance(data, list):
            return [Source(**d) for d in data if isinstance(d, dict)]
        return []

    def iter(self) -> Iterable[Source]:
        """Iterate over all available data sources.
        
        Yields
        ------
        Source
            Each available data source configuration.
            
        Examples
        --------
        >>> client = WebApiClient(base_url="http://localhost:8080/WebAPI")
        >>> for source in client.sources.iter():
        ...     print(f"Processing {source.sourceName}")
        """
        for s in self.list():
            yield s
