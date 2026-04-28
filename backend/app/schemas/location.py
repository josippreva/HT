from pydantic import BaseModel


class LocationBase(BaseModel):
    city_id: int
    postal_code_id: int
    name: str
    address: str | None = None
    note: str | None = None


class LocationCreate(LocationBase):
    pass


class LocationUpdate(LocationBase):
    pass


class LocationResponse(BaseModel):
    id: int
    city_id: int
    postal_code_id: int
    name: str
    address: str | None = None
    note: str | None = None

    city_name: str | None = None
    region_name: str | None = None
    postal_code: str | None = None
    postal_name: str | None = None

    class Config:
        from_attributes = True