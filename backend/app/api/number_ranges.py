from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import (
    NumberRange,
    RakNumberBlock,
    AreaCode,
    Location,
    City,
    Device,
)
from app.models import Region
from app.schemas.number_range import NumberRangeCreate, NumberRangeUpdate

router = APIRouter(prefix="/number-ranges", tags=["Number Ranges"])


def calculate_range_size(range_start: str, range_end: str) -> int:
    return int(range_end) - int(range_start) + 1


def validate_range_order(range_start: str, range_end: str) -> None:
    if int(range_start) >= int(range_end):
        raise HTTPException(
            status_code=400,
            detail="Početak raspona mora biti manji od kraja raspona",
        )


def validate_inside_rak_block(rak_block: RakNumberBlock, range_start: str, range_end: str) -> None:
    if int(range_start) < int(rak_block.block_start) or int(range_end) > int(rak_block.block_end):
        raise HTTPException(
            status_code=400,
            detail=f"Interni raspon mora biti unutar RAK bloka {rak_block.block_start} - {rak_block.block_end}",
        )


def check_internal_overlap(
    db: Session,
    range_start: str,
    range_end: str,
    exclude_id: int | None = None,
) -> None:
    query = db.query(NumberRange).filter(
        NumberRange.range_start <= range_end,
        NumberRange.range_end >= range_start,
    )

    if exclude_id:
        query = query.filter(NumberRange.id != exclude_id)

    existing = query.first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Interni raspon se preklapa s postojećim rasponom {existing.range_start} - {existing.range_end}",
        )


def validate_device_location(db: Session, device_id: int, location_id: int) -> None:
    device = db.query(Device).filter(Device.id == device_id).first()

    if not device:
        raise HTTPException(status_code=404, detail="Uređaj nije pronađen")

    if device.location_id != location_id:
        raise HTTPException(
            status_code=400,
            detail="Odabrani uređaj ne pripada odabranoj lokaciji",
        )


@router.get("")
def list_number_ranges(
    rak_block_id: int | None = Query(default=None),
    location_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = (
        db.query(NumberRange, RakNumberBlock, AreaCode, Location, City, Device)
        .join(RakNumberBlock, NumberRange.rak_block_id == RakNumberBlock.id)
        .join(AreaCode, RakNumberBlock.area_code_id == AreaCode.id)
        .join(Location, NumberRange.location_id == Location.id)
        .join(City, Location.city_id == City.id)
        .join(Device, NumberRange.device_id == Device.id)
    )

    if rak_block_id:
        query = query.filter(NumberRange.rak_block_id == rak_block_id)

    if location_id:
        query = query.filter(NumberRange.location_id == location_id)

    rows = query.order_by(NumberRange.range_start).all()

    return [
        {
            "id": number_range.id,
            "rak_block_id": number_range.rak_block_id,
            "location_id": number_range.location_id,
            "device_id": number_range.device_id,
            "name": number_range.name,
            "range_start": number_range.range_start,
            "range_end": number_range.range_end,
            "range_size": number_range.range_size,
            "generated": number_range.generated,
            "rak_block_start": rak_block.block_start,
            "rak_block_end": rak_block.block_end,
            "area_code": area_code.code,
            "location_name": location.name,
            "city_name": city.name,
            "device_name": device.name,
        }
        for number_range, rak_block, area_code, location, city, device in rows
    ]


@router.get("/{range_id}")
def get_number_range(range_id: int, db: Session = Depends(get_db)):
    row = (
        db.query(NumberRange, RakNumberBlock, AreaCode, Location, City, Device)
        .join(RakNumberBlock, NumberRange.rak_block_id == RakNumberBlock.id)
        .join(AreaCode, RakNumberBlock.area_code_id == AreaCode.id)
        .join(Location, NumberRange.location_id == Location.id)
        .join(City, Location.city_id == City.id)
        .join(Device, NumberRange.device_id == Device.id)
        .filter(NumberRange.id == range_id)
        .first()
    )

    if not row:
        raise HTTPException(status_code=404, detail="Interni raspon nije pronađen")

    number_range, rak_block, area_code, location, city, device = row

    return {
        "id": number_range.id,
        "rak_block_id": number_range.rak_block_id,
        "location_id": number_range.location_id,
        "device_id": number_range.device_id,
        "name": number_range.name,
        "range_start": number_range.range_start,
        "range_end": number_range.range_end,
        "range_size": number_range.range_size,
        "generated": number_range.generated,
        "rak_block_start": rak_block.block_start,
        "rak_block_end": rak_block.block_end,
        "area_code": area_code.code,
        "location_name": location.name,
        "city_name": city.name,
        "device_name": device.name,
    }


@router.post("", status_code=status.HTTP_201_CREATED)
def create_number_range(data: NumberRangeCreate, db: Session = Depends(get_db)):
    rak_block = db.query(RakNumberBlock).filter(RakNumberBlock.id == data.rak_block_id).first()
    if not rak_block:
        raise HTTPException(status_code=404, detail="RAK blok nije pronađen")

    location = db.query(Location).filter(Location.id == data.location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Lokacija nije pronađena")

    validate_rak_block_matches_location_region(db, rak_block, location)
    validate_range_order(data.range_start, data.range_end)
    validate_inside_rak_block(rak_block, data.range_start, data.range_end)
    check_internal_overlap(db, data.range_start, data.range_end)
    validate_device_location(db, data.device_id, data.location_id)

    number_range = NumberRange(
        rak_block_id=data.rak_block_id,
        location_id=data.location_id,
        device_id=data.device_id,
        name=data.name,
        range_start=data.range_start,
        range_end=data.range_end,
        range_size=calculate_range_size(data.range_start, data.range_end),
        generated=False,
    )

    db.add(number_range)
    db.commit()
    db.refresh(number_range)

    return number_range


@router.put("/{range_id}")
def update_number_range(
    range_id: int,
    data: NumberRangeUpdate,
    db: Session = Depends(get_db),
):
    number_range = db.query(NumberRange).filter(NumberRange.id == range_id).first()

    if not number_range:
        raise HTTPException(status_code=404, detail="Interni raspon nije pronađen")

    if number_range.generated:
        raise HTTPException(
            status_code=400,
            detail="Raspon koji je već generiran ne može se mijenjati",
        )

    rak_block = db.query(RakNumberBlock).filter(RakNumberBlock.id == data.rak_block_id).first()
    if not rak_block:
        raise HTTPException(status_code=404, detail="RAK blok nije pronađen")

    location = db.query(Location).filter(Location.id == data.location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Lokacija nije pronađena")

    validate_rak_block_matches_location_region(db, rak_block, location)
    validate_range_order(data.range_start, data.range_end)
    validate_inside_rak_block(rak_block, data.range_start, data.range_end)
    check_internal_overlap(db, data.range_start, data.range_end, exclude_id=range_id)
    validate_device_location(db, data.device_id, data.location_id)

    number_range.rak_block_id = data.rak_block_id
    number_range.location_id = data.location_id
    number_range.device_id = data.device_id
    number_range.name = data.name
    number_range.range_start = data.range_start
    number_range.range_end = data.range_end
    number_range.range_size = calculate_range_size(data.range_start, data.range_end)

    db.commit()
    db.refresh(number_range)

    return number_range


@router.delete("/{range_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_number_range(range_id: int, db: Session = Depends(get_db)):
    number_range = db.query(NumberRange).filter(NumberRange.id == range_id).first()

    if not number_range:
        raise HTTPException(status_code=404, detail="Interni raspon nije pronađen")

    if number_range.generated:
        raise HTTPException(
            status_code=400,
            detail="Raspon koji je već generiran ne može se obrisati",
        )

    db.delete(number_range)
    db.commit()

    return None


def validate_rak_block_matches_location_region(
    db: Session,
    rak_block: RakNumberBlock,
    location: Location,
) -> None:
    city = db.query(City).filter(City.id == location.city_id).first()

    if not city:
        raise HTTPException(status_code=404, detail="Grad lokacije nije pronađen")

    area_code = db.query(AreaCode).filter(AreaCode.id == rak_block.area_code_id).first()

    if not area_code:
        raise HTTPException(status_code=404, detail="Pozivni broj nije pronađen")

    if area_code.region_id != city.region_id:
        raise HTTPException(
            status_code=400,
            detail="RAK blok ne pripada županiji/regiji odabrane lokacije",
        )