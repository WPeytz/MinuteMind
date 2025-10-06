"""Database configuration and initialization."""
from sqlmodel import SQLModel


def init_db() -> None:
    """Create database tables and any startup logic."""
    # TODO: Configure engine and call SQLModel.metadata.create_all(engine)
    SQLModel.metadata
