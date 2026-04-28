from pydantic import BaseModel, field_validator


class DeviceBase(BaseModel):
    location_id: int
    name: str
    device_type: str
    serial_number: str | None = None
    active: bool = True

    @field_validator("device_type")
    @classmethod
    def validate_device_type(cls, value: str) -> str:
        allowed = {"MSAN", "GPON_OLT"}

        if value not in allowed:
            raise ValueError("Tip uređaja mora biti MSAN ili GPON_OLT")

        return value


class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(DeviceBase):
    pass


class DeviceResponse(BaseModel):
    id: int
    location_id: int
    name: str
    device_type: str
    serial_number: str | None = None
    active: bool

    location_name: str | None = None
    city_name: str | None = None

    class Config:
        from_attributes = True