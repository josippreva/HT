from pydantic import BaseModel


class AssignPhoneNumberRequest(BaseModel):
    subscriber_id: int
    note: str | None = None


class ReleasePhoneNumberRequest(BaseModel):
    note: str | None = None


class QuarantinePhoneNumberRequest(BaseModel):
    note: str | None = None