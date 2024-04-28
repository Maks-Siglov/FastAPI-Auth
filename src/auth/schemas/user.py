from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
)


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
    password: str | bytes = Field(alias="password")

    @field_validator("password")
    def password_validator(cls, v):
        if len(v) < 8 or len(v) > 24:
            raise ValueError(
                "Password length must be between 8 and 24 characters"
            )
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")

        if not any(char.isupper() for char in v):
            raise ValueError(
                "Password must contain at least one uppercase letter"
            )

        if not any(char.islower() for char in v):
            raise ValueError(
                "Password must contain at least one lowercase letter"
            )

        symbols = "!#$%&()*+,-.:;=?[]^_`{|}~"
        if not any(char in symbols for char in v):
            raise ValueError(
                "Password must contain at least one symbol:"
                " '!#$%&()*+,-.:;=?[]^_`{|}~'"
            )

        forbidden_symbols = "@\"'<>\\"
        if any(char in forbidden_symbols for char in v):
            raise ValueError(
                "Password cannot contain this symbols: '@\"'<>\\'"
            )

        return v
