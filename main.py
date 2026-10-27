from fastapi import FastAPI
from database import create_db
from routers.user_router import router as user_router

app=FastAPI()
app.include_router(user_router)
create_db()




