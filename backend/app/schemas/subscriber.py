from pydantic import BaseModel, EmailStr, field_validator, model_validator


class SubscriberBase(BaseModel):
    subscriber_type: str

    first_name: str | None = None
    last_name: str | None = None
    company_name: str | None = None

    jmbg: str | None = None
    company_id_number: str | None = None

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

    @field_validator("company_id_number")
    @classmethod
    def validate_company_id_number(cls, value: str | None) -> str | None:
        if value and (len(value) != 12 or not value.isdigit()):
          raise ValueError("ID broj firme mora imati točno 12 znamenki")

        return value



class SubscriberCreate(SubscriberBase):
    @model_validator(mode="after")
    def validate_required_fields(self):
        if self.subscriber_type == "physical_person":
            if not self.first_name:
                raise ValueError("Ime je obavezno za fizičko lice")

            if not self.last_name:
                raise ValueError("Prezime je obavezno za fizičko lice")

            if not self.jmbg:
                raise ValueError("JMBG je obavezan za fizičko lice")

        if self.subscriber_type == "legal_entity":
            if not self.company_name:
                raise ValueError("Naziv firme je obavezan za pravno lice")

            if not self.company_id_number:
                raise ValueError("ID broj firme je obavezan za pravno lice")

        if not self.address:
            raise ValueError("Adresa je obavezna")

        if not self.city_id:
            raise ValueError("Grad je obavezan")

        if not self.postal_code_id:
            raise ValueError("Poštanski broj je obavezan")

        if not self.contact_phone and not self.email:
            raise ValueError("Unesite kontakt telefon ili email")

        return self


class SubscriberUpdate(BaseModel):
    subscriber_type: str | None = None

    first_name: str | None = None
    last_name: str | None = None
    company_name: str | None = None

    jmbg: str | None = None
    company_id_number: str | None = None

    address: str | None = None
    city_id: int | None = None
    postal_code_id: int | None = None
    contact_phone: str | None = None
    email: EmailStr | None = None

    note: str | None = None

    @field_validator("subscriber_type")
    @classmethod
    def validate_subscriber_type(cls, value: str | None) -> str | None:
        if value is None:
            return value

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


class SubscriberOut(SubscriberBase):
    id: int
    city_name: str | None = None
    assigned_phone_numbers: list[str] = []

    model_config = {
        "from_attributes": True
    }