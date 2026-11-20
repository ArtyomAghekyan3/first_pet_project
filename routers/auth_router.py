
from fastapi import APIRouter,  status
from database import sessionDep,create_user
from schems import UserIn, UserOut



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
