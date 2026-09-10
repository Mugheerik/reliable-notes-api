from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from uuid import UUID

class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str


class NoteUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = None


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class NoteResponse(BaseModel):
    id: UUID
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    archived: bool
    owner_id: UUID