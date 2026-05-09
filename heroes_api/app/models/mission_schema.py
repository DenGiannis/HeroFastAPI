from pydantic import BaseModel, Field

class MissionCreateRequest(BaseModel):
    """Schema for creating a new mission."""
    title: str = Field(min_length=5)
    difficulty: int = Field(ge=1, le=10)
    hero_id: int

class MissionUpdateRequest(BaseModel):
    """Schema for updating an existing mission."""
    title: str | None = None
    difficulty: int | None = None
    completed: bool | None = None
    hero_id: int | None = None

class MissionResponse(BaseModel):
    """Schema for mission response."""
    id: int
    title: str
    difficulty: int
    completed: bool
    hero_id: int
