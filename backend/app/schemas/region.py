from pydantic import BaseModel


class RegionBase(BaseModel):
    entity_id: int
    name: str


class RegionCreate(RegionBase):
    pass


class RegionUpdate(RegionBase):
    pass


class RegionOut(RegionBase):
    id: int

    class Config:
        from_attributes = True