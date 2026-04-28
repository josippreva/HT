from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import Subscriber, PhoneNumber
from app.schemas.subscriber import SubscriberCreate, SubscriberUpdate

router = APIRouter(prefix="/subscribers", tags=["Subscribers"])


@router.get("")
def list_subscribers(
    search: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Subscriber)

    if search:
        value = f"%{search}%"
        query = query.filter(
            (Subscriber.first_name.ilike(value)) |
            (Subscriber.last_name.ilike(value)) |
            (Subscriber.company_name.ilike(value)) |
            (Subscriber.jmbg.ilike(value))
        )

    return query.order_by(Subscriber.id.desc()).all()


@router.get("/{subscriber_id}")
def get_subscriber(subscriber_id: int, db: Session = Depends(get_db)):
    subscriber = db.query(Subscriber).filter(Subscriber.id == subscriber_id).first()

    if not subscriber:
        raise HTTPException(status_code=404, detail="Pretplatnik nije pronađen")

    return subscriber


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

    for key, value in data.model_dump().items():
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