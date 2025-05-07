from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from db import Base

class DeviceGroup(Base):
    __tablename__ = "device_groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    devices = relationship("Device", back_populates="group")

class Device(Base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True, index=True)
    model = Column(String, index=True)
    os_version = Column(String)
    hostname = Column(String)
    serial_number = Column(String)
    group_id = Column(Integer, ForeignKey("device_groups.id"), nullable=True)
    group = relationship("DeviceGroup", back_populates="devices")

class Advisory(Base):
    __tablename__ = "advisories"
    id = Column(Integer, primary_key=True, index=True)
    advisory_id = Column(String, unique=True, index=True)
    title = Column(String)
    severity = Column(String)
    publication_date = Column(Date)
    product = Column(String)
    description = Column(Text)

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    advisory_id = Column(Integer, ForeignKey("advisories.id"))
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    device = relationship("Device")
    advisory = relationship("Advisory")