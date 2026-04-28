from pydantic import BaseModel


class EntityResponse(BaseModel):
    id: int
    code: str
    name: str

    class Config:
        from_attributes = True


class RegionResponse(BaseModel):
    id: int
    entity_id: int
    name: str

    class Config:
        from_attributes = True


class CityResponse(BaseModel):
    id: int
    region_id: int
    name: str

    class Config:
        from_attributes = True


class PostalCodeResponse(BaseModel):
    id: int
    city_id: int
    postal_code: str
    postal_name: str

    class Config:
        from_attributes = True