from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator
)
from pydantic_core.core_schema import ValidationInfo

from auth.utils.password import validate_password


class UserLoginSchema(BaseModel):
    email: EmailStr = Field(alias="username")
    password: str


class BaseUserSchema(BaseModel):
    email: EmailStr


class UserSchema(BaseUserSchema):
    id: int
    is_active: bool = Field(default=True)

    class Config:
        from_attributes = True


class UserCreationSchema(BaseUserSchema):
    password: str = Field(alias="password")

    @field_validator("password")
    def password_validator(cls, password_field: str) -> str:
        return validate_password(password_field)


class ChangePasswordSchema(BaseModel):
    old_password: str
    new_password: str
    new_password_confirm: str

    @field_validator("new_password")
    def password_validator(cls, password_field: str) -> str:
        return validate_password(password_field)

    @field_validator("new_password_confirm")
    def validate_new_password_confirm(
        cls, password_field: str, validation_info: ValidationInfo
    ) -> str:
        values = validation_info.data
        if (
            "new_password" in values
            and password_field != values["new_password"]
        ):
            raise ValueError("New passwords do not match")
        return password_field
