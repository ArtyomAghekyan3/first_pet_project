
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException,  status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from database import sessionDep,create_user
from moduls import UsersModel
from schems import Token, UserIn, UserOut
from security import create_access_token, verify_password_func



router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED
)
def register_user(
    user_data: UserIn,
    session: sessionDep):

    new_user = create_user(
        email=user_data.email,
        firstname=user_data.firstname,
        lastname=user_data.lastname,
        password=user_data.password,
        session=session
    )
    
    return new_user



@router.post("/login", response_model=Token)
def login(
    form_data: Annotated[
        OAuth2PasswordRequestForm,
        Depends()
    ],
    session: sessionDep
):
    # 1. Ищем пользователя по email
    query = select(UsersModel).where(
        UsersModel.email == form_data.username.lower()
    )

    user =  session.scalar(query)

    # 2. Проверяем существование пользователя и пароль
    if user is None or not verify_password_func(
        form_data.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # 3. Создаём JWT
    access_token = create_access_token(user.id)

    # 4. Возвращаем токен
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
