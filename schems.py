from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field, EmailStr, StringConstraints, field_validator, model_validator


Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]

class BaseUser(BaseModel):
    email : EmailStr = Field( max_length=255)
    firstname: Name
    lastname: Name

class UpdateUser(BaseUser):
    email: EmailStr | None = None
    firstname: Name | None = None
    lastname: Name | None = None


class UserIn(BaseUser):
    password: str = Field( min_length=8, max_length=128)
    password_repeat: str


    @field_validator("email")
    @classmethod
    def email_validation(cls, value: str) -> str:
        result = value.lower()
        return result

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one digit.")
        if not any(char.isupper() for char in value):
            raise ValueError("Password must contain at least one uppercase letter.")
        return value

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.password_repeat:
            raise ValueError("Passwords do not match.")
        return self

class UserOut(BaseUser):
    model_config = ConfigDict(from_attributes=True)
    id: int
    