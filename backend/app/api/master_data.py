from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import Entity, Region, City, PostalCode
from app.api.deps import get_current_user
from app.schemas.master_data import (
    EntityResponse,
    RegionResponse,
    CityResponse,
    PostalCodeResponse,
)

router = APIRouter(tags=["Master Data"],dependencies=[Depends(get_current_user)])


@router.get("/regions", response_model=list[RegionResponse])
def get_regions(
    entity_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Region)

    if entity_id:
        query = query.filter(Region.entity_id == entity_id)

    return query.order_by(Region.name).all()


@router.get("/cities", response_model=list[CityResponse])
def get_cities(
    region_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(City)

    if region_id:
        query = query.filter(City.region_id == region_id)

    return query.order_by(City.name).all()


@router.get("/postal-codes", response_model=list[PostalCodeResponse])
def get_postal_codes(
    city_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(PostalCode)

    if city_id:
        query = query.filter(PostalCode.city_id == city_id)

    return query.order_by(PostalCode.postal_code).all()



@router.get("/entities", response_model=list[EntityResponse])
def get_entities(db: Session = Depends(get_db)):
    return db.query(Entity).order_by(Entity.name).all()