
from database import  get_user,sessionDep,delete_user, update_user
from schems import UpdateUser, UserOut
from fastapi import APIRouter


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/get_user/{user_id}",response_model=UserOut)
def get_user_by_id_on_page(user_id:int,session:sessionDep):
    return get_user(user_id=user_id, session=session)


@router.delete("/delete_user/{user_id}")
def delete_user_by_id_on_page(user_id:int,session:sessionDep):
    return delete_user(user_id=user_id, session=session)


@router.patch("/update_user/{user_id}")
def update_user_by_id_on_page(user_id:int,data:UpdateUser,session:sessionDep):
    user=update_user(
        user_id=user_id,
        data=data.model_dump(exclude_unset=True),
        session=session
        )
    session.commit()
    return {"message":"User updated successfully","user_id":user.id}


   
    
    
