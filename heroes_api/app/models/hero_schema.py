from pydantic import BaseModel, Field

class HeroCreateRequest(BaseModel):
    """Schema for creating a new hero."""
    name: str = Field(min_length=3)
    power: str = Field(min_length=3)

class HeroUpdateRequest(BaseModel):
    """Schema for updating an existing hero."""
    name: str | None = Field(default=None, min_length=3)
    power: str | None = Field(default=None, min_length=3)
    level: int | None = Field(default=None, ge=1, le=100)
    active: bool | None = Field(default=None)

class HeroResponse(BaseModel):
    """Schema for hero response."""
    id: int
    name: str
    power: str
    level: int
    active: bool