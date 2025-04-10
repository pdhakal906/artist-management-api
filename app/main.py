from fastapi import FastAPI
from auth.routes.auth import router as user_router
from routes.artist import router as artist_router

app = FastAPI(title="Artist Management")


app.get("/")(lambda: {"message": "API call successful"})


app.include_router(user_router, tags=["User APIs"])
app.include_router(artist_router, tags=["Artist APIs"])
