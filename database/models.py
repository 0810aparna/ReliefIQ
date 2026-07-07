"""
Tables matching what the project actually uses: real Kerala district data,
infrastructure, 2018 disaster history, plus logged predictions/decisions/
allocations generated at runtime via the API.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from database.base import Base


class District(Base):
    __tablename__ = "districts"
    district_id = Column(Integer, primary_key=True)
    district_name = Column(String, nullable=False)
    state = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    population = Column(Integer)


class Infrastructure(Base):
    __tablename__ = "infrastructure"
    district_id = Column(Integer, primary_key=True)
    hospitals = Column(Integer)
    shelters = Column(Integer)
    roads = Column(Integer)
    rescue_centers = Column(Integer)


class DisasterHistory(Base):
    __tablename__ = "disaster_history"
    disaster_id = Column(Integer, primary_key=True, autoincrement=True)
    district_id = Column(Integer, nullable=False)
    actual_rainfall_in_mm = Column(Float)
    normal_rainfall_in_mm = Column(Float)
    no_of_landslides = Column(Integer)
    full_damaged_houses = Column(Integer)
    fatalities = Column(Integer)
    severity = Column(String)
    rainfall_pct_of_normal = Column(Float)
    rainfall_deviation_from_normal = Column(Float)


class PredictionLog(Base):
    __tablename__ = "predictions"
    prediction_id = Column(Integer, primary_key=True, autoincrement=True)
    district_id = Column(Integer, nullable=False)
    severity = Column(String)
    risk_score = Column(Float)
    confidence = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class DecisionLog(Base):
    __tablename__ = "decisions_log"
    decision_id = Column(Integer, primary_key=True, autoincrement=True)
    district_id = Column(Integer, nullable=False)
    prediction_id = Column(Integer)
    action = Column(String)
    alert_level = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class ResourceInventory(Base):
    __tablename__ = "resource_inventory"
    resource_id = Column(Integer, primary_key=True, autoincrement=True)
    resource_name = Column(String, nullable=False)
    available_quantity = Column(Float)


class Allocation(Base):
    __tablename__ = "allocation"
    allocation_id = Column(Integer, primary_key=True, autoincrement=True)
    district_id = Column(Integer, nullable=False)
    resource_id = Column(Integer)
    quantity = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())