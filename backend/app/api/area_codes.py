from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import AreaCode, Entity, Region, City
from app.api.deps import get_current_user
router = APIRouter(prefix="/area-codes", tags=["Area Codes"],dependencies=[Depends(get_current_user)])


@router.get("")
def list_area_codes(
    entity_id: int | None = Query(default=None),
    region_id: int | None = Query(default=None),
    city_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = (
        db.query(AreaCode, Entity, Region, City)
        .join(Entity, AreaCode.entity_id == Entity.id)
        .join(Region, AreaCode.region_id == Region.id)
        .outerjoin(City, AreaCode.city_id == City.id)
    )

    if entity_id:
        query = query.filter(AreaCode.entity_id == entity_id)

    if region_id:
        query = query.filter(AreaCode.region_id == region_id)

    if city_id:
        query = query.filter(AreaCode.city_id == city_id)

    rows = query.order_by(Entity.name, Region.name, AreaCode.code).all()

    return [
        {
            "id": area_code.id,
            "entity_id": area_code.entity_id,
            "region_id": area_code.region_id,
            "city_id": area_code.city_id,
            "code": area_code.code,
            "name": area_code.name,
            "entity_name": entity.name,
            "region_name": region.name,
            "city_name": city.name if city else None,
        }
        for area_code, entity, region, city in rows
    ]