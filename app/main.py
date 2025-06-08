from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import upload, convert, split, convert_svc, train, auth
import os

app = FastAPI()

# 프론트엔드 URL 설정
frontend_url = os.getenv("FRONTEND_URL", "https://vocal-alchemy-mixer.lovable.app")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    # 특정 프론트엔드 URL과 로컬 개발 환경 허용
    allow_origins=[
        frontend_url,
        "https://vocal-alchemy-mixer.lovable.app",
        "http://localhost:3000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # 모든 메소드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

# 라우터 설정
app.include_router(auth.router, prefix="/auth")
app.include_router(upload.router, prefix="/upload")
app.include_router(convert.router, prefix="/convert")
app.include_router(split.router, prefix="/audio")
app.include_router(convert_svc.router, prefix="/svc")
app.include_router(train.router, prefix="/train")

# 기본 라우트
@app.get("/")
async def root():
    return {"message": "API is running"}
