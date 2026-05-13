from pydantic import BaseModel

from app.schemas.subscriber import SubscriberCreate


class AssignPhoneNumberRequest(BaseModel):
    subscriber_id: int
    public_id: str | None = None
    private_id: str | None = None
    domain: str | None = None
    note: str | None = None


class AssignPhoneNumberWithSubscriberRequest(BaseModel):
    subscriber: SubscriberCreate
    public_id: str | None = None
    private_id: str | None = None
    domain: str | None = None
    note: str | None = None

class ReleasePhoneNumberRequest(BaseModel):
    note: str | None = None


class QuarantinePhoneNumberRequest(BaseModel):
    note: str | None = None