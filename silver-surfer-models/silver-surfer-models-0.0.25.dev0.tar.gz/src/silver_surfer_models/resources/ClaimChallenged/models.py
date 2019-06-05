from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)

from ...database import Base


class ClaimChallengedModel(Base):
    __tablename__ = 'claims_challenged'

    id = Column(Integer, primary_key=True)
    trial_id = Column(
        Integer,
        ForeignKey('trials.id'),
        nullable=False,
    )
    claim_id = Column(
        Integer,
        ForeignKey('claims.id'),
        nullable=False,
    )
    prior_art_combination = Column(
        Integer,
        nullable=False,
    )
    prior_art_id = Column(
        Integer,
        ForeignKey('prior_arts.id'),
        nullable=False,
    )
    prior_art_nature = Column(String(128))
    updated_at = Column(DateTime, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            'trial_id',
            'claim_id',
            'prior_art_combination',
            'prior_art_id',
        ),
    )
