from pydantic import BaseModel

from app.schemas.subscriber import SubscriberCreate


class AssignPhoneNumberRequest(BaseModel):
    subscriber_id: int
    note: str | None = None


class AssignPhoneNumberWithSubscriberRequest(BaseModel):
    subscriber: SubscriberCreate
    note: str | None = None


class ReleasePhoneNumberRequest(BaseModel):
    note: str | None = None


class QuarantinePhoneNumberRequest(BaseModel):
    note: str | None = None