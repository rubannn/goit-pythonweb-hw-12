from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UserResponse(UserBase):
    id: int
    is_verified: bool
    avatar_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class RequestEmail(BaseModel):
    email: EmailStr
