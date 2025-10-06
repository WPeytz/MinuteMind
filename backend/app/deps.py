"""Common dependency utilities for FastAPI routes."""
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager


@asynccontextmanager
def get_db() -> AsyncIterator[None]:
    """Yield a database session instance.

    Replace the body with integration against the actual database engine.
    """
    # TODO: Plug in real database session lifecycle management.
    yield
