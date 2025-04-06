from fastapi import FastAPI
from routes.users import router as user_router

app = FastAPI()


app.get("/")(lambda: {"message": "API call successful"})

app.include_router(user_router, tags=["User APIs"])
