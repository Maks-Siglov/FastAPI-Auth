from pydantic import (
    BaseModel,
    EmailStr,
    Field
)


class BaseUserSchema(BaseModel):
    email: EmailStr


class UserCreationSchema(BaseUserSchema):
    password: str | bytes = Field(alias="password")


class UserSchema(BaseUserSchema):
    id: int
    is_active: bool = Field(default=True)

    class Config:
        from_attributes = True
