from fastapi import APIRouter, Body, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src import schemas
from src.db import models
from src.db.database import get_session

router = APIRouter()


# ----------------------
# Device Registration
# ----------------------
@router.post("/register")
async def register_device(
    raw_id: str = Body(..., media_type="text/plain"),
    db: AsyncSession = Depends(get_session),
):
    # clean whitespace
    device_id = raw_id.strip()

    # Check if exists
    device = await models.Device.get_by_id(db, device_id)
    if device:
        if device.approved:
            return {"status": "already_registered"}
        else:
            raise HTTPException(status_code=401, detail="Device still not registered.")

    # Create new device
    device = models.Device(id=device_id)
    db.add(device)
    await db.commit()

    raise HTTPException(
        status_code=401, detail="Device not registered. Wait for approval."
    )


# ----------------------
# Send Data
# ----------------------
@router.post("/send_data")
async def send_data(
    values: list[schemas.SensorValueIn],
    sensor_id: str = Header(None, alias="X-SENSOR-ID"),
    db: AsyncSession = Depends(get_session),
):
    if sensor_id is None:
        raise HTTPException(status_code=400, detail="Missing X-SENSOR-ID header")

    device = await models.Device.get_by_id(db, sensor_id)
    if not device:
        raise HTTPException(
            status_code=401, detail="Device not registered. Call /register first."
        )

    for entry in values:
        # check or create sensor
        sensor = await models.Sensor.get_sensor(
            db, device_id=device.id, name=entry.sensor
        )
        if not sensor:
            sensor = models.Sensor(
                name=entry.sensor, type=entry.type, device_id=device.id
            )
            db.add(sensor)
            await db.flush()  # get sensor id

        # store reading
        reading = models.SensorReading(
            sensor_id=sensor.id,
            raw_value=entry.value,
            shift=entry.shift,
            normalized=entry.normalized(),
        )
        db.add(reading)

    await db.commit()
    return {"status": "ok", "count": len(values)}
