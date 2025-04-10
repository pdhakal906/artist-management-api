from fastapi import FastAPI, Depends
from fastapi.security import APIKeyHeader
from auth.routes.auth import router as user_router
from routes.artist import router as artist_router
from auth.jwt import decode_access_token

app = FastAPI(title="Artist Management")

app.get("/")(lambda: {"message": "API call successful"})


app.include_router(user_router, tags=["User APIs"])
app.include_router(
    artist_router,
    tags=["Artist APIs"],
    dependencies=[Depends(decode_access_token)],
)
