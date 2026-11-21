from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(190), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    saved_locations = relationship("SavedLocation", back_populates="user", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="user", cascade="all, delete-orphan")

class City(Base):
    __tablename__ = "cities"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    country: Mapped[str] = mapped_column(String(120), default="")
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    timezone: Mapped[str] = mapped_column(String(80), default="UTC")
    locations = relationship("MonitoringLocation", back_populates="city", cascade="all, delete-orphan")
    __table_args__ = (UniqueConstraint("name", "country", "latitude", "longitude", name="uq_city_coordinates"),)

class MonitoringLocation(Base):
    __tablename__ = "monitoring_locations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id", ondelete="CASCADE"))
    label: Mapped[str] = mapped_column(String(160), default="City centre")
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    city = relationship("City", back_populates="locations")
    readings = relationship("AirQualityReading", back_populates="location", cascade="all, delete-orphan")

class Pollutant(Base):
    __tablename__ = "pollutants"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    unit: Mapped[str] = mapped_column(String(30), default="µg/m³")

class AirQualityReading(Base):
    __tablename__ = "air_quality_readings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("monitoring_locations.id", ondelete="CASCADE"), index=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    source: Mapped[str] = mapped_column(String(60), default="Open-Meteo")
    location = relationship("MonitoringLocation", back_populates="readings")
    values = relationship("PollutantValue", back_populates="reading", cascade="all, delete-orphan")

class PollutantValue(Base):
    __tablename__ = "pollutant_values"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reading_id: Mapped[int] = mapped_column(ForeignKey("air_quality_readings.id", ondelete="CASCADE"), index=True)
    pollutant_id: Mapped[int] = mapped_column(ForeignKey("pollutants.id"))
    value: Mapped[float] = mapped_column(Float)
    reading = relationship("AirQualityReading", back_populates="values")
    pollutant = relationship("Pollutant")
    __table_args__ = (UniqueConstraint("reading_id", "pollutant_id", name="uq_reading_pollutant"),)

class Alert(Base):
    __tablename__ = "alerts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    pollutant_code: Mapped[str] = mapped_column(String(20))
    threshold: Mapped[float] = mapped_column(Float)
    enabled: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="alerts")

class SavedLocation(Base):
    __tablename__ = "saved_locations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("monitoring_locations.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="saved_locations")
    location = relationship("MonitoringLocation")
    __table_args__ = (UniqueConstraint("user_id", "location_id", name="uq_user_saved_location"),)
