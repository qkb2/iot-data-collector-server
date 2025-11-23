from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    func,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship
from src.db.database import Base


class Device(Base):
    __tablename__ = "devices"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)

    sensors = relationship("Sensor", back_populates="device", cascade="all, delete")

    # --- helpers ---
    @staticmethod
    async def get_by_id(db: AsyncSession, device_id: str):
        result = await db.execute(select(Device).where(Device.id == device_id))
        return result.scalar_one_or_none()

    async def save(self, db: AsyncSession):
        db.add(self)
        await db.commit()
        await db.refresh(self)


class Sensor(Base):
    __tablename__ = "sensors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    device_id = Column(String, ForeignKey("devices.id"))
    device = relationship("Device", back_populates="sensors")

    readings = relationship(
        "SensorReading", back_populates="sensor", cascade="all, delete"
    )

    @staticmethod
    async def get_sensor(db: AsyncSession, device_id: str, name: str):
        stmt = (
            select(Sensor)
            .where(Sensor.device_id == device_id)
            .where(Sensor.name == name)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def save(self, db: AsyncSession):
        db.add(self)
        await db.commit()
        await db.refresh(self)


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    sensor_id = Column(Integer, ForeignKey("sensors.id"))
    sensor = relationship("Sensor", back_populates="readings")

    async def save(self, db: AsyncSession):
        db.add(self)
        await db.commit()
