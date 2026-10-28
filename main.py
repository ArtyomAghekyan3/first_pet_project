from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from database import create_db
from routers.user_router import router as user_router
from routers.documents_router import router as documents_router

app=FastAPI()
app.include_router(user_router)
app.include_router(documents_router)
