from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
)

from ...database import Base


class ClaimDependencyModel(Base):
    __tablename__ = 'claim_dependencies'

    id = Column(Integer, primary_key=True)
    claim_id = Column(
        Integer,
        ForeignKey('claims.id'),
        nullable=False,
    )
    parent_claim_id = Column(
        Integer,
        ForeignKey('claims.id'),
        nullable=False,
    )
    updated_at = Column(DateTime, nullable=False)
