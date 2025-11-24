from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db import models
from src.db.database import get_session

router = APIRouter(prefix="/frontend", tags=["frontend"])


# ----------------------------
# DEVICES
# ----------------------------
@router.get("/devices")
async def list_devices(db: AsyncSession = Depends(get_session)):
    stmt = select(models.Device).order_by(models.Device.id)
    result = await db.execute(stmt)
    devices = result.scalars().all()

    return [
        {
            "id": d.id,
            "sensor_count": len(d.sensors),
        }
        for d in devices
    ]


@router.get("/devices/{device_id}")
async def device_detail(device_id: str, db: AsyncSession = Depends(get_session)):
    device = await models.Device.get_by_id(db, device_id)
    if not device:
        raise HTTPException(404, "Device not found")

    return {
        "id": device.id,
        "sensors": [
            {
                "id": s.id,
                "name": s.name,
                "type": s.type,
            }
            for s in device.sensors
        ],
    }


@router.delete("/devices/{device_id}")
async def delete_device(device_id: str, db: AsyncSession = Depends(get_session)):
    device = await models.Device.get_by_id(db, device_id)
    if not device:
        raise HTTPException(404, "Device not found")

    await db.delete(device)
    await db.commit()
    return {"status": "deleted", "id": device_id}


# ----------------------------
# SENSORS
# ----------------------------
@router.get("/sensors")
async def list_sensors(db: AsyncSession = Depends(get_session)):
    stmt = select(models.Sensor)
    result = await db.execute(stmt)
    sensors = result.scalars().all()

    return [
        {
            "id": s.id,
            "name": s.name,
            "type": s.type,
            "device_id": s.device_id,
        }
        for s in sensors
    ]


@router.get("/sensors/{sensor_id}")
async def sensor_detail(sensor_id: int, db: AsyncSession = Depends(get_session)):
    sensor = await db.get(models.Sensor, sensor_id)
    if not sensor:
        raise HTTPException(404, "Sensor not found")

    return {
        "id": sensor.id,
        "name": sensor.name,
        "type": sensor.type,
        "device_id": sensor.device_id,
        "reading_count": len(sensor.readings),
    }


@router.delete("/sensors/{sensor_id}")
async def delete_sensor(sensor_id: int, db: AsyncSession = Depends(get_session)):
    sensor = await db.get(models.Sensor, sensor_id)
    if not sensor:
        raise HTTPException(404, "Sensor not found")

    await db.delete(sensor)
    await db.commit()

    return {"status": "deleted", "id": sensor_id}


# ----------------------------
# READINGS
# ----------------------------
@router.get("/sensors/{sensor_id}/readings")
async def list_readings(
    sensor_id: int,
    limit: int = 50,
    db: AsyncSession = Depends(get_session),
):
    sensor = await db.get(models.Sensor, sensor_id)
    if not sensor:
        raise HTTPException(404, "Sensor not found")

    stmt = (
        select(models.SensorReading)
        .where(models.SensorReading.sensor_id == sensor_id)
        .order_by(desc(models.SensorReading.id))
        .limit(limit)
    )

    result = await db.execute(stmt)
    readings = result.scalars().all()

    return [
        {
            "id": r.id,
            "raw_value": r.raw_value,
            "shift": r.shift,
            "normalized": r.normalized,
        }
        for r in readings
    ]


@router.post("/devices/{device_id}/approve")
async def approve_device(device_id: str, db: AsyncSession = Depends(get_session)):
    device = await models.Device.get_by_id(db, device_id)
    if not device:
        raise HTTPException(404, "Device not found")

    device.approved = True
    await db.commit()

    return {"status": "approved", "id": device_id}
