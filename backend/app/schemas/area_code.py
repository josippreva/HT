from pydantic import BaseModel


class AreaCodeResponse(BaseModel):
    id: int
    entity_id: int
    region_id: int
    city_id: int | None = None
    code: str
    name: str

    entity_name: str | None = None
    region_name: str | None = None
    city_name: str | None = None

    class Config:
        from_attributes = True