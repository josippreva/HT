from pydantic import BaseModel, field_validator


class NumberRangeBase(BaseModel):
    rak_block_id: int
    location_id: int
    device_id: int | None = None
    name: str | None = None
    range_start: str
    range_end: str

    @field_validator("range_start", "range_end")
    @classmethod
    def only_digits(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("Broj mora sadržavati samo znamenke")
        return value


class NumberRangeCreate(NumberRangeBase):
    pass


class NumberRangeUpdate(NumberRangeBase):
    pass