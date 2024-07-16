from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from pydantic_core.core_schema import ValidationInfo

from src.api.v1.users.utils.password import validate_password


class BaseUserSchema(BaseModel):
    email: EmailStr = Field(description="Email address of the user.")


class UserLoginSchema(BaseUserSchema):
    password: str


class UserSchema(BaseUserSchema):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool = Field(
        default=True, description="Whether the user is active."
    )


class UserResponseSchema(UserSchema):
    model_config = ConfigDict(from_attributes=True)

    first_name: str = Field(description="First name of the user.")
    last_name: str = Field(description="Last name of the user.")
    balance: int = Field(description="Balance of the user.")

    created_at: datetime = Field(description="The date the user was created.")
    updated_at: datetime = Field(
        description="The date the user was last updated."
    )


class UsersResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    users: list[UserResponseSchema] | list


class UserCreationSchema(BaseUserSchema):
    password: str = Field(
        description="Password for the user account (8-24 characters, "
        "containing at least one digit, uppercase letter, lowercase letter, "
        "and special character).",
        min_length=8,
        max_length=24,
    )

    @field_validator("password")
    def password_validator(cls, password_field: str) -> str:
        return validate_password(password_field)


class ChangePasswordSchema(BaseModel):
    old_password: str = Field(
        min_length=8, max_length=24, description="Old user password."
    )
    new_password: str = Field(
        min_length=8, max_length=24, description="New user password."
    )
    new_password_confirm: str = Field(
        min_length=8,
        max_length=24,
        description="New user password confirmation.",
    )

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
