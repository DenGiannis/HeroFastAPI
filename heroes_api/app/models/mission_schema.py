from pydantic import BaseModel, Field

class MissionCreateRequest(BaseModel):
    """Schema for creating a new mission."""
    title: str = Field(min_length=5)
    difficulty: int = Field(ge=1, le=10)
    hero_id: int

class MissionUpdateRequest(BaseModel):
    """Schema for updating an existing mission."""
    title: str | None = Field(default=None, min_length=5)
    difficulty: int | None = Field(default=None, ge=1, le=10)
    completed: bool | None = Field(default=None)
    hero_id: int | None = Field(default=None)

class MissionResponse(BaseModel):
    """Schema for mission response."""
    id: int
    title: str
    difficulty: int
    completed: bool
    hero_id: int
