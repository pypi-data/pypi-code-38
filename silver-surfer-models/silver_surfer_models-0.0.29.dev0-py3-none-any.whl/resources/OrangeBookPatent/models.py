from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    UniqueConstraint,
)

from ...database import Base


class OrangeBookPatentModel(Base):
    __tablename__ = 'orange_book_patents'

    id = Column(Integer, primary_key=True)
    appl_no = Column(String(128))
    appl_type = Column(String(128))
    delist_flag = Column(String(128))
    drug_product_flag = Column(String(128))
    drug_substance_flag = Column(String(128))
    patent_no = Column(String(128), nullable=False)
    patent_use_code = Column(String(128))
    product_no = Column(String(128), nullable=False)
    patent_expire_date = Column(DateTime)
    submission_date = Column(DateTime)
    updated_at = Column(DateTime)

    __table_args__ = (UniqueConstraint('patent_no', 'product_no'),)
