from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import Region, Entity
from app.schemas.region import RegionCreate, RegionUpdate
from app.api.deps import get_current_user
router = APIRouter(prefix="/regions", tags=["Regions"],dependencies=[Depends(get_current_user)])


def validate_entity(db: Session, entity_id: int):
    entity = db.query(Entity).filter(Entity.id == entity_id).first()

    if not entity:
        raise HTTPException(status_code=404, detail="Entitet nije pronađen")


@router.get("")
def list_regions(entity_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Region)

    if entity_id is not None:
        query = query.filter(Region.entity_id == entity_id)

    return query.order_by(Region.name).all()


@router.get("/{region_id}")
def get_region(region_id: int, db: Session = Depends(get_db)):
    region = db.query(Region).filter(Region.id == region_id).first()

    if not region:
        raise HTTPException(status_code=404, detail="Regija nije pronađena")

    return region


@router.post("", status_code=status.HTTP_201_CREATED)
def create_region(data: RegionCreate, db: Session = Depends(get_db)):
    validate_entity(db, data.entity_id)

    region = Region(
        entity_id=data.entity_id,
        name=data.name,
    )

    db.add(region)
    db.commit()
    db.refresh(region)

    return region


@router.put("/{region_id}")
def update_region(region_id: int, data: RegionUpdate, db: Session = Depends(get_db)):
    region = db.query(Region).filter(Region.id == region_id).first()

    if not region:
        raise HTTPException(status_code=404, detail="Regija nije pronađena")

    validate_entity(db, data.entity_id)

    region.entity_id = data.entity_id
    region.name = data.name

    db.commit()
    db.refresh(region)

    return region


@router.delete("/{region_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_region(region_id: int, db: Session = Depends(get_db)):
    region = db.query(Region).filter(Region.id == region_id).first()

    if not region:
        raise HTTPException(status_code=404, detail="Regija nije pronađena")

    db.delete(region)
    db.commit()

    return None