from pydantic import BaseModel, EmailStr, field_validator


class SubscriberBase(BaseModel):
    subscriber_type: str

    first_name: str | None = None
    last_name: str | None = None
    company_name: str | None = None

    jmbg: str | None = None

    address: str | None = None
    city_id: int | None = None
    postal_code_id: int | None = None
    contact_phone: str | None = None
    email: EmailStr | None = None

    note: str | None = None

    @field_validator("subscriber_type")
    @classmethod
    def validate_subscriber_type(cls, value: str) -> str:
        allowed = {"physical_person", "legal_entity"}

        if value not in allowed:
            raise ValueError("Tip pretplatnika mora biti physical_person ili legal_entity")

        return value

    @field_validator("jmbg")
    @classmethod
    def validate_jmbg(cls, value: str | None) -> str | None:
        if value and (len(value) != 13 or not value.isdigit()):
            raise ValueError("JMBG mora imati točno 13 znamenki")

        return value


class SubscriberCreate(SubscriberBase):
    pass


class SubscriberUpdate(SubscriberBase):
    pass


class SubscriberOut(SubscriberBase):
    id: int
    assigned_phone_numbers: list[str] = []

    class Config:
        from_attributes = True