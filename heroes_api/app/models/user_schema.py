from pydantic import BaseModel, Field

class UserCreateRequest(BaseModel):
    """Schema for creating a new user."""
    username: str = Field(min_length=3)
    password: str = Field(min_length=6)
    is_admin: bool = Field(default=False)

class UserUpdateRequest(BaseModel):
    """Schema for updating an existing user."""
    username: str | None = None
    password: str | None = None

class UserResponse(BaseModel):
    """Schema for user response."""
    id: int
    username: str
    is_admin: bool
