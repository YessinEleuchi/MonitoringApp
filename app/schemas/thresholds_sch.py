from pydantic import BaseModel

class ThresholdsBase(BaseModel):
    critical_success_rate: float
    critical_latency: float
    test_frequency_minutes: int

class ThresholdsCreate(ThresholdsBase):
    pass

class ThresholdsUpdate(ThresholdsBase):
    pass

class ThresholdsOut(ThresholdsBase):
    id: int

    class Config:
        from_attributes = True
