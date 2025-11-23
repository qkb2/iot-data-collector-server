from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src import schemas
from src.db import models
from src.db.database import get_session

router = APIRouter()


# ---------------------------------------------------------
#  POST /api/register
# ---------------------------------------------------------
@router.post("/register", response_model=schemas.DeviceOut)
async def register_device(
    payload: schemas.DeviceRegister, db: AsyncSession = Depends(get_session)
):
    existing = await models.Device.get_by_id(db, payload.id)

    if existing:
        return existing

    device = models.Device(id=payload.id, name=payload.id)
    await device.save(db)

    for s in payload.sensors:
        sensor = models.Sensor(name=s, device_id=device.id)
        await sensor.save(db)

    return device


# ---------------------------------------------------------
#  POST /api/send_data
# ---------------------------------------------------------
@router.post("/send_data")
async def send_sensor_data(
    payload: schemas.SensorDataIn, db: AsyncSession = Depends(get_session)
):
    device = await models.Device.get_by_id(db, payload.id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Device not registered"
        )

    for entry in payload.sensor_values:
        sensor = await models.Sensor.get_sensor(db, device.id, entry.name)
        if not sensor:
            continue  # ignore unknown sensors

        reading = models.SensorReading(sensor_id=sensor.id, value=float(entry.value))
        await reading.save(db)

    return {"status": "ok"}
