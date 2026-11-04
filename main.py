from fastapi import FastAPI

from routers.user_router import router as user_router
from routers.documents_router import router as documents_router
import uvicorn

app=FastAPI()
app.include_router(user_router)
app.include_router(documents_router)

if __name__=="__main__":
    uvicorn.run('main:app', host="0.0.0.0", port=8000)
