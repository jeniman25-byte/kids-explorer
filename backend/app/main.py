from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.middleware.auth import AuthMiddleware
from app.routers import image, parse, subject, tts, vision

app = FastAPI(title="KidsExplorer API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuthMiddleware)

app.include_router(parse.router)
app.include_router(image.router)
app.include_router(vision.router)
app.include_router(tts.router)
app.include_router(subject.router)


@app.get("/health")
async def health():
    return {"success": True, "message": "ok"}
