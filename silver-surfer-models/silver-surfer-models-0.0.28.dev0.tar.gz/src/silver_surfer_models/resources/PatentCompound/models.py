from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)

from ...database import Base


class PatentCompoundModel(Base):
    __tablename__ = 'patent_compounds'

    id = Column(Integer, primary_key=True)
    patent_id = Column(
        Integer,
        ForeignKey('patents.id'),
        nullable=False,
    )
    cid = Column(String(128), nullable=False)
    compound_name = Column(String(256), nullable=False)
    iupac_name = Column(String(256), nullable=False)
    molecular_formula = Column(String(256), nullable=False)
    molecular_weight = Column(String(256), nullable=False)
    structure_file_id = Column(
        Integer,
        ForeignKey('files.id'),
        nullable=False,
    )

    updated_at = Column(DateTime)

    __table_args__ = (UniqueConstraint('patent_id', 'cid'),)
