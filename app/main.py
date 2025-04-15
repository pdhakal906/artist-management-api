import os
from fastapi import FastAPI, Depends, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from fastapi.staticfiles import StaticFiles
from auth.routes.auth import router as user_router
from routes.artist import router as artist_router
from routes.music import router as music_router
from auth.jwt import decode_access_token


app = FastAPI(
    title="Artist Management",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)
api_router = APIRouter(prefix="/api")

origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("static_files", exist_ok=True)

app.mount("/static", StaticFiles(directory="static_files"), name="static")

api_router.get("/")(lambda: {"message": "API call successful"})

api_router.include_router(user_router, tags=["User APIs"])
api_router.include_router(
    artist_router,
    tags=["Artist APIs"],
    dependencies=[Depends(decode_access_token)],
)
api_router.include_router(
    music_router,
    tags=["Music APIs"],
    dependencies=[Depends(decode_access_token)],
)


app.include_router(api_router)
