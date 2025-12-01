from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    func,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.database import Base


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    sensors: Mapped[list["Sensor"]] = relationship(back_populates="device")
    approved: Mapped[bool] = mapped_column(Boolean, default=False)

    @staticmethod
    async def get_by_id(db: AsyncSession, device_id: str):
        stmt = select(Device).where(Device.id == device_id)
        res = await db.execute(stmt)
        return res.scalar_one_or_none()


class Sensor(Base):
    __tablename__ = "sensors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)
    type: Mapped[str] = mapped_column(String)
    device_id: Mapped[str] = mapped_column(ForeignKey("devices.id"))

    device: Mapped["Device"] = relationship(back_populates="sensors")
    readings: Mapped[list["SensorReading"]] = relationship(back_populates="sensor")

    @staticmethod
    async def get_sensor(db: AsyncSession, device_id: str, name: str):
        stmt = select(Sensor).where(Sensor.device_id == device_id, Sensor.name == name)
        res = await db.execute(stmt)
        return res.scalar_one_or_none()


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sensor_id: Mapped[int] = mapped_column(ForeignKey("sensors.id"))
    raw_value: Mapped[int] = mapped_column(Integer)
    shift: Mapped[int] = mapped_column(Integer)
    normalized: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    sensor: Mapped["Sensor"] = relationship(back_populates="readings")
