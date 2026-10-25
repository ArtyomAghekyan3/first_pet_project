from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator



class BaseUser(BaseModel):
    email : EmailStr = Field( max_length=255)
    firstname: str = Field( max_length=100)
    lastname:str = Field( max_length=100)


class UserIn(BaseUser):
    password: str = Field( min_length=8, max_length=128)
    password_repeat: str = Field( min_length=8, max_length=128)

    
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
    pass
    