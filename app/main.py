from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from auth.routes.auth import router as user_router
from routes.artist import router as artist_router
from routes.music import router as music_router
from auth.jwt import decode_access_token

app = FastAPI(title="Artist Management")
origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.get("/")(lambda: {"message": "API call successful"})

app.include_router(user_router, tags=["User APIs"])
app.include_router(
    artist_router,
    tags=["Artist APIs"],
    dependencies=[Depends(decode_access_token)],
)
app.include_router(
    music_router,
    tags=["Music APIs"],
    dependencies=[Depends(decode_access_token)],
)
