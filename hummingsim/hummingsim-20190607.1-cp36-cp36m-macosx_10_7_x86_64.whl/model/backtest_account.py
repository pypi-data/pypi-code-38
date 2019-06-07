#!/usr/bin/env python

from sqlalchemy import (
    Column,
    VARCHAR,
    Integer,
)
from sqlalchemy.orm import relationship

from . import HummingbotBase


class BacktestAccount(HummingbotBase):
    __tablename__ = "BacktestAccount"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(VARCHAR(255), nullable=False, unique=True, index=True)
    assets = relationship("BacktestAccountAsset", back_populates="account")

    def __repr__(self) -> str:
        return f"BacktestAccount(name='{self.name}')"
