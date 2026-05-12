from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, aliased

from app.db.database import get_db
from app.models import Subscriber, PhoneNumber, NumberRange, Location, City, Region
from app.schemas.subscriber import SubscriberCreate, SubscriberUpdate, SubscriberOut
from app.api.deps import get_current_user

router = APIRouter(prefix="/subscribers", tags=["Subscribers"],dependencies=[Depends(get_current_user)])


def subscriber_to_dict(subscriber: Subscriber, phone_numbers: list[str] | None = None):
    return {
        "id": subscriber.id,
        "subscriber_type": subscriber.subscriber_type,
        "first_name": subscriber.first_name,
        "last_name": subscriber.last_name,
        "company_name": subscriber.company_name,
        "jmbg": subscriber.jmbg,
        "company_id_number": subscriber.company_id_number,
        "address": subscriber.address,
        "city_id": subscriber.city_id,
        "city_name": subscriber.city.name if subscriber.city else None,
        "postal_code_id": subscriber.postal_code_id,
        "contact_phone": subscriber.contact_phone,
        "email": subscriber.email,
        "note": subscriber.note,
        "assigned_phone_numbers": phone_numbers or [],
    }


@router.get("", response_model=list[SubscriberOut])
def list_subscribers(
    search: str | None = Query(default=None),
    region_id: int | None = Query(default=None),
    city_id: int | None = Query(default=None),
    location_id: int | None = Query(default=None),
    device_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    SubscriberCity = aliased(City)

    query = (
        db.query(Subscriber)
        .outerjoin(SubscriberCity, Subscriber.city_id == SubscriberCity.id)
        .outerjoin(PhoneNumber, PhoneNumber.subscriber_id == Subscriber.id)
        .outerjoin(NumberRange, PhoneNumber.number_range_id == NumberRange.id)
        .outerjoin(Location, NumberRange.location_id == Location.id)
    )

    if search:
        value = f"%{search.strip()}%"
        full_name = Subscriber.first_name + " " + Subscriber.last_name

        query = query.filter(
            (Subscriber.first_name.ilike(value)) |
            (Subscriber.last_name.ilike(value)) |
            (full_name.ilike(value)) |
            (Subscriber.company_name.ilike(value)) |
            (Subscriber.jmbg.ilike(value)) |
            (PhoneNumber.number_value.ilike(value))
        )

    # OVO filtrira grad/regiju PRETPLATNIKA
    if region_id:
        query = query.filter(SubscriberCity.region_id == region_id)

    if city_id:
        query = query.filter(Subscriber.city_id == city_id)

    # OVO filtrira samo one koji imaju dodijeljeni broj na toj lokaciji/uređaju
    if location_id:
        query = query.filter(Location.id == location_id)

    if device_id:
        query = query.filter(NumberRange.device_id == device_id)

    subscribers = query.distinct().order_by(Subscriber.id.desc()).all()
    subscriber_ids = [subscriber.id for subscriber in subscribers]

    phone_numbers_by_subscriber = {
        subscriber_id: []
        for subscriber_id in subscriber_ids
    }

    if subscriber_ids:
        phone_numbers = (
            db.query(PhoneNumber)
            .filter(PhoneNumber.subscriber_id.in_(subscriber_ids))
            .order_by(PhoneNumber.number_value)
            .all()
        )

        for phone in phone_numbers:
            phone_numbers_by_subscriber[phone.subscriber_id].append(phone.number_value)

    return [
        subscriber_to_dict(
            subscriber,
            phone_numbers_by_subscriber.get(subscriber.id, []),
        )
        for subscriber in subscribers
    ]

@router.get("/{subscriber_id}", response_model=SubscriberOut)
def get_subscriber(subscriber_id: int, db: Session = Depends(get_db)):
    subscriber = db.query(Subscriber).filter(Subscriber.id == subscriber_id).first()

    if not subscriber:
        raise HTTPException(status_code=404, detail="Pretplatnik nije pronađen")

    phone_numbers = (
        db.query(PhoneNumber)
        .filter(PhoneNumber.subscriber_id == subscriber_id)
        .order_by(PhoneNumber.number_value)
        .all()
    )

    return subscriber_to_dict(
        subscriber,
        [phone.number_value for phone in phone_numbers],
    )


@router.post("", status_code=status.HTTP_201_CREATED)
def create_subscriber(data: SubscriberCreate, db: Session = Depends(get_db)):
    subscriber = Subscriber(**data.model_dump())

    db.add(subscriber)
    db.commit()
    db.refresh(subscriber)

    return subscriber


@router.put("/{subscriber_id}")
def update_subscriber(
    subscriber_id: int,
    data: SubscriberUpdate,
    db: Session = Depends(get_db),
):
    subscriber = db.query(Subscriber).filter(Subscriber.id == subscriber_id).first()

    if not subscriber:
        raise HTTPException(status_code=404, detail="Pretplatnik nije pronađen")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(subscriber, key, value)

    db.commit()
    db.refresh(subscriber)

    return subscriber


@router.delete("/{subscriber_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subscriber(subscriber_id: int, db: Session = Depends(get_db)):
    subscriber = db.query(Subscriber).filter(Subscriber.id == subscriber_id).first()

    if not subscriber:
        raise HTTPException(status_code=404, detail="Pretplatnik nije pronađen")

    has_numbers = (
        db.query(PhoneNumber)
        .filter(PhoneNumber.subscriber_id == subscriber_id)
        .first()
    )

    if has_numbers:
        raise HTTPException(
            status_code=400,
            detail="Pretplatnik ima dodijeljene brojeve i ne može se obrisati",
        )

    db.delete(subscriber)
    db.commit()

    return None