from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, BigInteger, Boolean, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()


class Device(Base):
    __tablename__ = 'devices'

    uuid = Column(String, primary_key=True, nullable=False)
    capacity = Column(BigInteger, nullable=False)
    operational = Column(Boolean, nullable=False, default=True)
    name = Column(String, nullable=True)

    files = relationship("File", back_populates="device")

    def __repr__(self):
        return '<device {}>'.format(self.uuid)


class File(Base):
    __tablename__ = 'files'

    path = Column(String, nullable=False, primary_key=True)
    last_modified = Column(BigInteger, nullable=False, primary_key=True)

    device_id = Column(String, ForeignKey('devices.uuid', ondelete='CASCADE'), nullable=False)
    device = relationship("Device", back_populates="files")
    hash = Column(String, nullable=False)
    size = Column(BigInteger, nullable=False)
    outdated = Column(Boolean, nullable=False, default=False)

    def __repr__(self):
        return "<File {}/'{}', modified {}>".format(self.device, self.path, self.last_modified)
