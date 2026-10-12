from sqlalchemy import Column, DateTime, Integer, String
from app.database import Base


class SyncState(Base):
    """When each external source was last synced into the local DB."""

    __tablename__ = "sync_state"

    source = Column(String, primary_key=True)  # e.g. "cafenomad:taipei"
    synced_at = Column(DateTime, nullable=False)
    row_count = Column(Integer, default=0)
