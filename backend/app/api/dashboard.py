from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import get_db
from app.models import (
    Location,
    Device,
    NumberRange,
    RakNumberBlock,
    Subscriber,
    PhoneNumber,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total = db.query(func.count(PhoneNumber.id)).scalar()

    free = db.query(func.count(PhoneNumber.id)).filter(
        PhoneNumber.status == "slobodan"
    ).scalar()

    busy = db.query(func.count(PhoneNumber.id)).filter(
        PhoneNumber.status == "zauzet"
    ).scalar()

    quarantine = db.query(func.count(PhoneNumber.id)).filter(
        PhoneNumber.status == "karantena"
    ).scalar()

    ranges_total = db.query(func.count(NumberRange.id)).scalar()

    ranges_generated = db.query(func.count(NumberRange.id)).filter(
        NumberRange.generated == True
    ).scalar()

    ranges_not_generated = db.query(func.count(NumberRange.id)).filter(
        NumberRange.generated == False
    ).scalar()

    return {
        "locations": db.query(func.count(Location.id)).scalar(),
        "devices": db.query(func.count(Device.id)).scalar(),
        "ranges": ranges_total,
        "ranges_generated": ranges_generated,
        "ranges_not_generated": ranges_not_generated,
        "rak_blocks": db.query(func.count(RakNumberBlock.id)).scalar(),
        "subscribers": db.query(func.count(Subscriber.id)).scalar(),
        "phone_numbers_total": total,
        "free": free,
        "busy": busy,
        "quarantine": quarantine,
    }