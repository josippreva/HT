from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import Device, Location, City, Region, Entity
from app.schemas.device import DeviceCreate, DeviceUpdate

router = APIRouter(prefix="/devices", tags=["Devices"])


@router.get("")
def list_devices(
    entity_id: int | None = Query(default=None),
    region_id: int | None = Query(default=None),
    city_id: int | None = Query(default=None),
    location_id: int | None = Query(default=None),
    active: bool | None = Query(default=None),
    search: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = (
        db.query(Device, Location, City, Region, Entity)
        .join(Location, Device.location_id == Location.id)
        .join(City, Location.city_id == City.id)
        .join(Region, City.region_id == Region.id)
        .join(Entity, Region.entity_id == Entity.id)
    )

    if entity_id:
        query = query.filter(Entity.id == entity_id)

    if region_id:
        query = query.filter(Region.id == region_id)

    if city_id:
        query = query.filter(City.id == city_id)

    if location_id:
        query = query.filter(Location.id == location_id)

    if active is not None:
        query = query.filter(Device.active == active)

    if search:
        search_value = f"%{search}%"
        query = query.filter(
            (Device.name.ilike(search_value)) |
            (Device.serial_number.ilike(search_value))
        )

    rows = query.order_by(Entity.name, Region.name, City.name, Location.name, Device.name).all()

    return [
        {
            "id": device.id,
            "location_id": device.location_id,
            "name": device.name,
            "device_type": device.device_type,
            "serial_number": device.serial_number,
            "active": device.active,
            "location_name": location.name,
            "city_id": city.id,
            "city_name": city.name,
            "region_id": region.id,
            "region_name": region.name,
            "entity_id": entity.id,
            "entity_name": entity.name,
        }
        for device, location, city, region, entity in rows
    ]

@router.get("/{device_id}")
def get_device(device_id: int, db: Session = Depends(get_db)):
    row = (
        db.query(Device, Location, City, Region, Entity)
        .join(Location, Device.location_id == Location.id)
        .join(City, Location.city_id == City.id)
        .join(Region, City.region_id == Region.id)
        .join(Entity, Region.entity_id == Entity.id)
        .filter(Device.id == device_id)
        .first()
    )

    if not row:
        raise HTTPException(status_code=404, detail="Uređaj nije pronađen")

    device, location, city, region, entity = row

    return {
        "id": device.id,
        "location_id": device.location_id,
        "name": device.name,
        "device_type": device.device_type,
        "serial_number": device.serial_number,
        "active": device.active,

        "location_name": location.name,
        "city_id": city.id,
        "city_name": city.name,
        "region_id": region.id,
        "region_name": region.name,
        "entity_id": entity.id,
        "entity_name": entity.name,
    }


@router.post("", status_code=status.HTTP_201_CREATED)
def create_device(data: DeviceCreate, db: Session = Depends(get_db)):
    location = db.query(Location).filter(Location.id == data.location_id).first()

    if not location:
        raise HTTPException(status_code=404, detail="Lokacija nije pronađena")

    device = Device(
        location_id=data.location_id,
        name=data.name,
        device_type=data.device_type,
        serial_number=data.serial_number,
        active=data.active,
    )

    db.add(device)
    db.commit()
    db.refresh(device)

    return device


@router.put("/{device_id}")
def update_device(device_id: int, data: DeviceUpdate, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.id == device_id).first()

    if not device:
        raise HTTPException(status_code=404, detail="Uređaj nije pronađen")

    location = db.query(Location).filter(Location.id == data.location_id).first()

    if not location:
        raise HTTPException(status_code=404, detail="Lokacija nije pronađena")

    device.location_id = data.location_id
    device.name = data.name
    device.device_type = data.device_type
    device.serial_number = data.serial_number
    device.active = data.active

    db.commit()
    db.refresh(device)

    return device


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_device(device_id: int, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.id == device_id).first()

    if not device:
        raise HTTPException(status_code=404, detail="Uređaj nije pronađen")

    db.delete(device)
    db.commit()

    return None