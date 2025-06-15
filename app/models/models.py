from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Table
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    
    licenses = relationship("License", back_populates="owner")

class License(Base):
    __tablename__ = "licenses"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    allowed_ips = Column(String)  # เก็บเป็น comma-separated string
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    owner = relationship("User", back_populates="licenses")
    activations = relationship("Activation", back_populates="license")

class Activation(Base):
    __tablename__ = "activations"

    id = Column(Integer, primary_key=True, index=True)
    license_id = Column(Integer, ForeignKey("licenses.id"))
    ip_address = Column(String)
    machine_id = Column(String)
    activated_at = Column(DateTime, default=datetime.utcnow)
    last_check_in = Column(DateTime, default=datetime.utcnow)
    
    license = relationship("License", back_populates="activations")