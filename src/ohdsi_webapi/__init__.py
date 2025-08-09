"""OHDSI WebAPI Python Client."""

# Load environment variables from .env file (if present)
from .env import load_env
load_env()

from .client import WebApiClient

__all__ = ["WebApiClient"]

__version__ = "0.1.0"
