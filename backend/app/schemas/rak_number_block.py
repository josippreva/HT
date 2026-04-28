from pydantic import BaseModel, field_validator


class RakNumberBlockBase(BaseModel):
    area_code_id: int
    operator_name: str
    block_start: str
    block_end: str
    source_file: str | None = None

    @field_validator("block_start", "block_end")
    @classmethod
    def only_digits(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("Broj mora sadržavati samo znamenke")
        return value


class RakNumberBlockCreate(RakNumberBlockBase):
    pass


class RakNumberBlockResponse(BaseModel):
    id: int
    area_code_id: int
    operator_name: str
    block_start: str
    block_end: str
    block_size: int
    source_file: str | None = None

    area_code: str | None = None
    area_name: str | None = None
    region_name: str | None = None

    class Config:
        from_attributes = True