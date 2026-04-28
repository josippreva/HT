from pydantic import BaseModel


class CityBase(BaseModel):
    region_id: int
    name: str


class CityCreate(CityBase):
    pass


class CityUpdate(CityBase):
    pass


class CityOut(CityBase):
    id: int

    class Config:
        from_attributes = True