"""
Service layer for F1 application business logic.

This layer provides independently testable business logic separate from HTTP routing.
Services handle data processing and calculations without HTTP dependencies.
"""
from .f1_service import F1Service

__all__ = ["F1Service"]
