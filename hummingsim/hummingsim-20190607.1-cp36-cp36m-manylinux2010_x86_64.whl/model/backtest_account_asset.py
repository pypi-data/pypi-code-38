#!/usr/bin/env python

from sqlalchemy import (
    Column,
    VARCHAR,
    Integer,
    Numeric,
    ForeignKey,
    Index
)
from sqlalchemy.orm import relationship

from . import HummingbotBase


class BacktestAccountAsset(HummingbotBase):
    __tablename__ = "BacktestAccountAsset"
    __table_args__ = (Index("account_asset_index", "account_id", "symbol", unique=True),)

    id = Column(Integer, primary_key=True, nullable=False)
    symbol = Column(VARCHAR(255), nullable=False)
    amount = Column(Numeric(precision=65, scale=18), nullable=False)
    account_id = Column(Integer, ForeignKey("BacktestAccount.id"), nullable=False)
    account = relationship("BacktestAccount", back_populates="assets")

    def __repr__(self) -> str:
        return f"BacktestAccountAsset(symbol='{self.symbol}', amount={self.amount}, account_id={self.account_id})"
