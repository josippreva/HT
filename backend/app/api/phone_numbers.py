from datetime import datetime, timezone
import re

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import PhoneNumber, NumberRange, Location, City, Region, Entity, Device, Subscriber
from app.api.deps import get_current_user
from app.schemas.phone_number_actions import (
    AssignPhoneNumberRequest,
    ReleasePhoneNumberRequest,
    QuarantinePhoneNumberRequest,
    AssignPhoneNumberWithSubscriberRequest,
)

router = APIRouter(prefix="/phone-numbers", tags=["Phone Numbers"],dependencies=[Depends(get_current_user)])






def get_last_six_digits(number: str) -> str:
    digits = re.sub(r"\D", "", str(number))
    return digits[-6:].zfill(6)


def is_all_same(value: str) -> bool:
    return len(set(value)) == 1


def is_repeating_pattern(value: str, size: int) -> bool:
    if len(value) % size != 0:
        return False

    pattern = value[:size]
    return pattern * (len(value) // size) == value


def is_increasing_sequence(value: str) -> bool:
    return all(int(value[i + 1]) == int(value[i]) + 1 for i in range(len(value) - 1))


def classify_phone_number(number: str) -> str:
    value = get_last_six_digits(number)

    a, b, c, d, e, f = value

    # =====================
    # PREMIUM
    # =====================

    # XXX XXX / XYZ XYZ
    if value[:3] == value[3:]:
        return "premium"

    # XXX YYY
    if len(set(value[:3])) == 1 and len(set(value[3:])) == 1:
        return "premium"

    # XXX 000
    if len(set(value[:3])) == 1 and value[3:] == "000":
        return "premium"

    # 000 XXX
    if value[:3] == "000" and len(set(value[3:])) == 1:
        return "premium"

    # X00 X00
    if b == "0" and c == "0" and e == "0" and f == "0" and a == d:
        return "premium"

    # X0 X0 X0
    if b == "0" and d == "0" and f == "0" and a == c == e:
        return "premium"

    # 0X 0X 0X
    if a == "0" and c == "0" and e == "0" and b == d == f:
        return "premium"

    # XY XY XY
    if value[:2] * 3 == value:
        return "premium"

    # =====================
    # GOLD
    # =====================

    # XYY YYY
    if b == c == d == e == f and a != b:
        return "gold"

    # XXX XXY
    if a == b == c == d == e and f != a:
        return "gold"

    # X00 Y00
    if b == c == "0" and e == f == "0" and a != d:
        return "gold"

    # X00 000
    if b == c == d == e == f == "0" and a != "0":
        return "gold"

    # 000 00X
    if a == b == c == d == e == "0" and f != "0":
        return "gold"

    # X0 Y0 Z0
    if b == d == f == "0":
        return "gold"

    # 00X 00Y
    if a == b == "0" and d == e == "0":
        return "gold"

    # 6*(X+1), npr. 123456
    if is_increasing_sequence(value):
        return "gold"

    # =====================
    # SILVER
    # =====================

    # XY0 000
    if c == "0" and d == e == f == "0" and a != b:
        return "silver"

    # XXY YYY
    if a == b and c == d == e == f and a != c:
        return "silver"

    # XXX XYY
    if a == b == c == d and e == f and d != e:
        return "silver"

    # 000 0XX
    if a == b == c == d == "0" and e == f and e != "0":
        return "silver"

    # XX0 000
    if a == b and c == d == e == f == "0":
        return "silver"

    # X00 00X
    if b == c == d == e == "0" and a == f and a != "0":
        return "silver"

    # XX YY ZZ
    if a == b and c == d and e == f:
        return "silver"

    # =====================
    # BRONZE
    # =====================

    # XYZ 000
    if d == e == f == "0":
        return "bronze"

    # 000 XYZ
    if a == b == c == "0":
        return "bronze"

    # 000 0XY
    if a == b == c == d == "0":
        return "bronze"

    # XYZ ZYX
    if a == f and b == e and c == d:
        return "bronze"

    # 3*(X+1) 3*(Y+1), npr. 123234
    first = value[:3]
    second = value[3:]

    if (
        is_increasing_sequence(first)
        and is_increasing_sequence(second)
        and int(second[0]) == int(first[0]) + 1
    ):
        return "bronze"

    # 3*(X+1) 3*(X-1), npr. 123210
    if (
        is_increasing_sequence(first)
        and all(int(second[i + 1]) == int(second[i]) - 1 for i in range(2))
    ):
        return "bronze"

    return "standard"







@router.post("/generate/{number_range_id}", status_code=status.HTTP_201_CREATED)
def generate_phone_numbers(number_range_id: int, db: Session = Depends(get_db)):
    number_range = db.query(NumberRange).filter(NumberRange.id == number_range_id).first()

    if not number_range:
        raise HTTPException(status_code=404, detail="Interni raspon nije pronađen")

    if number_range.generated:
        raise HTTPException(status_code=400, detail="Brojevi su već generirani za ovaj raspon")

    start = int(number_range.range_start)
    end = int(number_range.range_end)
    count = end - start + 1

    if count > 100000:
        raise HTTPException(status_code=400, detail="Maksimalno je dozvoljeno generirati 100.000 brojeva odjednom")

    numbers = [
        PhoneNumber(
            number_range_id=number_range.id,
            number_value=str(value),
            number_category=classify_phone_number(str(value)),
            status="slobodan",
        )
        for value in range(start, end + 1)
    ]

    db.add_all(numbers)
    number_range.generated = True

    db.commit()

    return {
        "message": f"Generirano {count} brojeva",
        "count": count,
    }


@router.get("")
def list_phone_numbers(
    entity_id: int | None = Query(default=None),
    region_id: int | None = Query(default=None),
    city_id: int | None = Query(default=None),
    location_id: int | None = Query(default=None),
    device_id: int | None = Query(default=None),
    number_range_id: int | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    number_category: str | None = Query(default=None),
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    query = (
        db.query(PhoneNumber, NumberRange, Location, City, Region, Entity, Subscriber)
        .join(NumberRange, PhoneNumber.number_range_id == NumberRange.id)
        .join(Location, NumberRange.location_id == Location.id)
        .join(City, Location.city_id == City.id)
        .join(Region, City.region_id == Region.id)
        .join(Entity, Region.entity_id == Entity.id)
        .outerjoin(Subscriber, PhoneNumber.subscriber_id == Subscriber.id)
    )

    if entity_id:
        query = query.filter(Entity.id == entity_id)

    if region_id:
        query = query.filter(Region.id == region_id)

    if city_id:
        query = query.filter(City.id == city_id)

    if location_id:
        query = query.filter(Location.id == location_id)

    if device_id:
        query = query.filter(NumberRange.device_id == device_id)

    if number_range_id:
        query = query.filter(PhoneNumber.number_range_id == number_range_id)

    if status_filter:
        query = query.filter(PhoneNumber.status == status_filter)

    if number_category:
        query = query.filter(PhoneNumber.number_category == number_category)

    if search:
        value = f"%{search}%"

        full_name = Subscriber.first_name + " " + Subscriber.last_name

        query = query.filter(
            (PhoneNumber.number_value.ilike(value)) |
            (Subscriber.first_name.ilike(value)) |
            (Subscriber.last_name.ilike(value)) |
            (full_name.ilike(value)) | 
            (Subscriber.company_name.ilike(value)) |
            (Subscriber.oib.ilike(value)) |
            (Subscriber.jmbg.ilike(value)) 
           #(Subscriber.external_id.ilike(value))
        )

    total = query.count()

    stats_rows = (
        query.with_entities(
            PhoneNumber.status,
            func.count(PhoneNumber.id),
        )
        .group_by(PhoneNumber.status)
        .all()
    )

    stats = {
        "total": total,
        "free": 0,
        "busy": 0,
        "quarantine": 0,
    }

    for status_name, count in stats_rows:
        if status_name == "slobodan":
            stats["free"] = count
        elif status_name == "zauzet":
            stats["busy"] = count
        elif status_name == "karantena":
            stats["quarantine"] = count

    rows = (
        query.order_by(PhoneNumber.number_value)
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page,
        "stats": stats,
        "data": [
            {
                "id": phone.id,
                "number_range_id": phone.number_range_id,
                "subscriber_id": phone.subscriber_id,
                "number_value": phone.number_value,
                "number_category": phone.number_category,
                "status": phone.status,
                "assigned_at": phone.assigned_at,
                "quarantine_at": phone.quarantine_at,
                "note": phone.note,

                "entity_id": entity.id,
                "entity_name": entity.name,
                "region_id": region.id,
                "region_name": region.name,
                "city_id": city.id,
                "city_name": city.name,
                "location_id": location.id,
                "location_name": location.name,

                "device_id": number_range.device_id,
                "range_start": number_range.range_start,
                "range_end": number_range.range_end,

                "subscriber_name": (
                    subscriber.company_name
                    if subscriber and subscriber.subscriber_type == "legal_entity"
                    else f"{subscriber.first_name or ''} {subscriber.last_name or ''}".strip()
                    if subscriber
                    else None
                ),
                "subscriber_oib": subscriber.oib if subscriber else None,
                "subscriber_jmbg": subscriber.jmbg if subscriber else None,
                #"subscriber_external_id": subscriber.external_id if subscriber else None,
            }
            for phone, number_range, location, city, region, entity, subscriber in rows
        ],
    }


@router.get("/{phone_number_id}")
def get_phone_number(phone_number_id: int, db: Session = Depends(get_db)):
    row = (
        db.query(PhoneNumber, NumberRange, Location, City, Subscriber)
        .join(NumberRange, PhoneNumber.number_range_id == NumberRange.id)
        .join(Location, NumberRange.location_id == Location.id)
        .join(City, Location.city_id == City.id)
        .outerjoin(Subscriber, PhoneNumber.subscriber_id == Subscriber.id)
        .filter(PhoneNumber.id == phone_number_id)
        .first()
    )

    if not row:
        raise HTTPException(status_code=404, detail="Broj nije pronađen")

    phone, number_range, location, city, subscriber = row

    return {
        "id": phone.id,
        "number_range_id": phone.number_range_id,
        "subscriber_id": phone.subscriber_id,
        "number_value": phone.number_value,
        "number_category": phone.number_category,
        "status": phone.status,
        "assigned_at": phone.assigned_at,
        "quarantine_at": phone.quarantine_at,
        "note": phone.note,
        "location_name": location.name,
        "city_name": city.name,
        "range_start": number_range.range_start,
        "range_end": number_range.range_end,
        "subscriber_name": (
            subscriber.company_name
            if subscriber and subscriber.subscriber_type == "legal_entity"
            else f"{subscriber.first_name or ''} {subscriber.last_name or ''}".strip()
            if subscriber
            else None
        ),
        "subscriber_oib": subscriber.oib if subscriber else None,
        "subscriber_jmbg": subscriber.jmbg if subscriber else None,
        #"subscriber_external_id": subscriber.external_id if subscriber else None,
    }


@router.post("/{phone_number_id}/assign")
def assign_phone_number(
    phone_number_id: int,
    data: AssignPhoneNumberRequest,
    db: Session = Depends(get_db),
):
    phone = db.query(PhoneNumber).filter(PhoneNumber.id == phone_number_id).first()

    if not phone:
        raise HTTPException(status_code=404, detail="Broj nije pronađen")

    if phone.status == "zauzet":
        raise HTTPException(status_code=400, detail="Broj je već zauzet")

    subscriber = db.query(Subscriber).filter(Subscriber.id == data.subscriber_id).first()

    if not subscriber:
        raise HTTPException(status_code=404, detail="Pretplatnik nije pronađen")

    validate_subscriber_matches_number_city(db, phone, subscriber)

    phone.subscriber_id = subscriber.id
    phone.status = "zauzet"
    phone.assigned_at = datetime.now(timezone.utc)
    phone.quarantine_at = None
    phone.note = data.note

    db.commit()
    db.refresh(phone)

    return phone



@router.post("/{phone_number_id}/assign-with-new-subscriber")
def assign_phone_number_with_new_subscriber(
    phone_number_id: int,
    data: AssignPhoneNumberWithSubscriberRequest,
    db: Session = Depends(get_db),
):
    phone = db.query(PhoneNumber).filter(PhoneNumber.id == phone_number_id).first()

    if not phone:
        raise HTTPException(status_code=404, detail="Broj nije pronađen")

    if phone.status == "zauzet":
        raise HTTPException(status_code=400, detail="Broj je već zauzet")

    if phone.status == "karantena":
        raise HTTPException(status_code=400, detail="Broj je u karanteni")

    subscriber = Subscriber(**data.subscriber.model_dump())

    db.add(subscriber)
    db.flush()

    validate_subscriber_matches_number_city(db, phone, subscriber)

    phone.subscriber_id = subscriber.id
    phone.status = "zauzet"
    phone.assigned_at = datetime.now(timezone.utc)
    phone.quarantine_at = None
    phone.note = data.note

    db.commit()
    db.refresh(phone)
    db.refresh(subscriber)

    return {
        "message": "Pretplatnik je kreiran i broj je uspješno dodijeljen",
        "phone_number_id": phone.id,
        "subscriber_id": subscriber.id,
    }




@router.post("/{phone_number_id}/release")
def release_phone_number(
    phone_number_id: int,
    data: ReleasePhoneNumberRequest,
    db: Session = Depends(get_db),
):
    phone = db.query(PhoneNumber).filter(PhoneNumber.id == phone_number_id).first()

    if not phone:
        raise HTTPException(status_code=404, detail="Broj nije pronađen")

    phone.subscriber_id = None
    phone.status = "slobodan"
    phone.assigned_at = None
    phone.quarantine_at = None
    phone.note = data.note

    db.commit()
    db.refresh(phone)

    return phone


@router.post("/{phone_number_id}/quarantine")
def quarantine_phone_number(
    phone_number_id: int,
    data: QuarantinePhoneNumberRequest,
    db: Session = Depends(get_db),
):
    phone = db.query(PhoneNumber).filter(PhoneNumber.id == phone_number_id).first()

    if not phone:
        raise HTTPException(status_code=404, detail="Broj nije pronađen")

    phone.subscriber_id = None
    phone.status = "karantena"
    phone.assigned_at = None
    phone.quarantine_at = datetime.now(timezone.utc)
    phone.note = data.note

    db.commit()
    db.refresh(phone)

    return phone


@router.post("/{phone_number_id}/activate")
def activate_phone_number(phone_number_id: int, db: Session = Depends(get_db)):
    phone = db.query(PhoneNumber).filter(PhoneNumber.id == phone_number_id).first()

    if not phone:
        raise HTTPException(status_code=404, detail="Broj nije pronađen")

    phone.subscriber_id = None
    phone.status = "slobodan"
    phone.assigned_at = None
    phone.quarantine_at = None

    db.commit()
    db.refresh(phone)

    return phone


def validate_subscriber_matches_number_city(
    db: Session,
    phone: PhoneNumber,
    subscriber: Subscriber,
) -> None:
    number_range = db.query(NumberRange).filter(
        NumberRange.id == phone.number_range_id
    ).first()

    if not number_range:
        raise HTTPException(status_code=404, detail="Raspon broja nije pronađen")

    location = db.query(Location).filter(
        Location.id == number_range.location_id
    ).first()

    if not location:
        raise HTTPException(status_code=404, detail="Lokacija raspona nije pronađena")

    if not subscriber.city_id:
        raise HTTPException(
            status_code=400,
            detail="Pretplatnik nema odabran grad/općinu",
        )

    if subscriber.city_id != location.city_id:
        raise HTTPException(
            status_code=400,
            detail="Pretplatnik nije iz grada/općine kojoj pripada ovaj broj",
        )



@router.post("/recalculate-categories")
def recalculate_categories(db: Session = Depends(get_db)):
    phones = db.query(PhoneNumber).all()

    updated = 0

    for phone in phones:
        phone.number_category = classify_phone_number(phone.number_value)
        updated += 1

    db.commit()

    return {
        "message": f"Kategorije ažurirane za {updated} brojeva"
    }        