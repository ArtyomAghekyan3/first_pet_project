
from typing import Annotated

from moduls import UsersModel
from auth.dependencies import get_current_user
from database import  get_user,sessionDep,delete_user, update_user
from schems import UpdateUser, UserOut
from fastapi import APIRouter, Depends


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/get_user/info",response_model=UserOut)
def get_user_by_id_on_page(current_user: Annotated[UsersModel, Depends(get_current_user)],
                           session: sessionDep):
    return get_user(user_id=current_user.id, session=session)


@router.delete("/delete_user")
def delete_user_by_id_on_page(current_user: Annotated[UsersModel, Depends(get_current_user)],
                               session: sessionDep):
    return delete_user(user_id=current_user.id, session=session)


@router.patch("/update_user")
def update_user_by_id_on_page(current_user: Annotated[UsersModel, Depends(get_current_user)],
                              data: UpdateUser,
                              session: sessionDep):
    user=update_user(
        user_id=current_user.id,
        data=data.model_dump(exclude_unset=True),
        session=session
        )
    session.commit()
    return {"message":"User updated successfully","user_id":user.id}


   
    
    
