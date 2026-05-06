from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import Location, City, PostalCode
from app.schemas.location import LocationCreate, LocationUpdate
from app.api.deps import get_current_user
router = APIRouter(prefix="/locations", tags=["Locations"],dependencies=[Depends(get_current_user)])


def validate_city_and_postal_code(db: Session, city_id: int, postal_code_id: int):
    city = db.query(City).filter(City.id == city_id).first()
    if not city:
        raise HTTPException(status_code=404, detail="Grad/općina nije pronađena")

    postal_code = db.query(PostalCode).filter(PostalCode.id == postal_code_id).first()
    if not postal_code:
        raise HTTPException(status_code=404, detail="Poštanski broj nije pronađen")

    if postal_code.city_id != city_id:
        raise HTTPException(
            status_code=400,
            detail="Poštanski broj ne pripada odabranom gradu/općini",
        )


@router.get("")
def list_locations(db: Session = Depends(get_db)):
    rows = (
        db.query(Location, City, PostalCode)
        .join(City, Location.city_id == City.id)
        .join(PostalCode, Location.postal_code_id == PostalCode.id)
        .order_by(Location.name)
        .all()
    )

    return [
        {
            "id": location.id,
            "city_id": location.city_id,
            "postal_code_id": location.postal_code_id,
            "name": location.name,
            "address": location.address,
            "note": location.note,
            "city_name": city.name,
            "postal_code": postal.postal_code,
            "postal_name": postal.postal_name,
        }
        for location, city, postal in rows
    ]


@router.get("/{location_id}")
def get_location(location_id: int, db: Session = Depends(get_db)):
    row = (
        db.query(Location, City, PostalCode)
        .join(City, Location.city_id == City.id)
        .join(PostalCode, Location.postal_code_id == PostalCode.id)
        .filter(Location.id == location_id)
        .first()
    )

    if not row:
        raise HTTPException(status_code=404, detail="Lokacija nije pronađena")

    location, city, postal = row

    return {
        "id": location.id,
        "city_id": location.city_id,
        "postal_code_id": location.postal_code_id,
        "name": location.name,
        "address": location.address,
        "note": location.note,
        "city_name": city.name,
        "postal_code": postal.postal_code,
        "postal_name": postal.postal_name,
    }


@router.post("", status_code=status.HTTP_201_CREATED)
def create_location(data: LocationCreate, db: Session = Depends(get_db)):
    validate_city_and_postal_code(db, data.city_id, data.postal_code_id)

    location = Location(
        city_id=data.city_id,
        postal_code_id=data.postal_code_id,
        name=data.name,
        address=data.address,
        note=data.note,
    )

    db.add(location)
    db.commit()
    db.refresh(location)

    return location


@router.put("/{location_id}")
def update_location(location_id: int, data: LocationUpdate, db: Session = Depends(get_db)):
    location = db.query(Location).filter(Location.id == location_id).first()

    if not location:
        raise HTTPException(status_code=404, detail="Lokacija nije pronađena")

    validate_city_and_postal_code(db, data.city_id, data.postal_code_id)

    location.city_id = data.city_id
    location.postal_code_id = data.postal_code_id
    location.name = data.name
    location.address = data.address
    location.note = data.note

    db.commit()
    db.refresh(location)

    return location


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_location(location_id: int, db: Session = Depends(get_db)):
    location = db.query(Location).filter(Location.id == location_id).first()

    if not location:
        raise HTTPException(status_code=404, detail="Lokacija nije pronađena")

    db.delete(location)
    db.commit()

    return None