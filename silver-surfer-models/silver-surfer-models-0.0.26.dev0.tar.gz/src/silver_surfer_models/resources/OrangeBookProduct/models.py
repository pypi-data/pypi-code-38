from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    UniqueConstraint,
)

from ...database import Base


class OrangeBookProductModel(Base):
    __tablename__ = 'orange_book_products'

    id = Column(Integer, primary_key=True)
    appl_no = Column(String(256), nullable=False)
    appl_type = Column(String(256))
    applicant = Column(String(256))
    applicant_full_name = Column(String(500))
    approval_date = Column(DateTime)
    dosage_form = Column(String(256))
    ingredient = Column(String(256))
    product_no = Column(String(128), nullable=False)
    rld = Column(String(256))
    rs = Column(String(256))
    route_of_administration = Column(String(256))
    strength = Column(String(500))
    te_code = Column(String(256))
    trade_name = Column(String(256))
    type = Column(String(256))
    updated_at = Column(DateTime)

    __table_args__ = (UniqueConstraint('appl_no', 'product_no'),)
