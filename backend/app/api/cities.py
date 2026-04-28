from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import City, Region
from app.schemas.city import CityCreate, CityUpdate

router = APIRouter(prefix="/cities", tags=["Cities"])


def validate_region(db: Session, region_id: int):
    region = db.query(Region).filter(Region.id == region_id).first()

    if not region:
        raise HTTPException(status_code=404, detail="Regija nije pronađena")


@router.get("")
def list_cities(region_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(City)

    if region_id is not None:
        query = query.filter(City.region_id == region_id)

    return query.order_by(City.name).all()


@router.get("/{city_id}")
def get_city(city_id: int, db: Session = Depends(get_db)):
    city = db.query(City).filter(City.id == city_id).first()

    if not city:
        raise HTTPException(status_code=404, detail="Grad/općina nije pronađena")

    return city


@router.post("", status_code=status.HTTP_201_CREATED)
def create_city(data: CityCreate, db: Session = Depends(get_db)):
    validate_region(db, data.region_id)

    city = City(
        region_id=data.region_id,
        name=data.name,
    )

    db.add(city)
    db.commit()
    db.refresh(city)

    return city


@router.put("/{city_id}")
def update_city(city_id: int, data: CityUpdate, db: Session = Depends(get_db)):
    city = db.query(City).filter(City.id == city_id).first()

    if not city:
        raise HTTPException(status_code=404, detail="Grad/općina nije pronađena")

    validate_region(db, data.region_id)

    city.region_id = data.region_id
    city.name = data.name

    db.commit()
    db.refresh(city)

    return city


@router.delete("/{city_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_city(city_id: int, db: Session = Depends(get_db)):
    city = db.query(City).filter(City.id == city_id).first()

    if not city:
        raise HTTPException(status_code=404, detail="Grad/općina nije pronađena")

    db.delete(city)
    db.commit()

    return None