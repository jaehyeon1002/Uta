from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import os
import importlib
import logging

# 로거 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# 동적으로 라우터 로드 및 설정
router_configs = [
    {"module": "app.routers.auth", "prefix": "/auth"},
    {"module": "app.routers.upload", "prefix": "/upload"},
    {"module": "app.routers.convert", "prefix": "/convert"},
    {"module": "app.routers.split", "prefix": "/audio"},
    {"module": "app.routers.convert_svc", "prefix": "/svc"},
    {"module": "app.routers.train", "prefix": "/train"},
]

for config in router_configs:
    try:
        module = importlib.import_module(config["module"])
        router = getattr(module, "router", None)
        if router and isinstance(router, APIRouter):
            app.include_router(router, prefix=config["prefix"])
            logger.info(f"라우터 로드 성공: {config['module']}")
        else:
            logger.warning(f"라우터를 찾을 수 없음: {config['module']}")
    except Exception as e:
        logger.error(f"라우터 로드 실패: {config['module']} - {str(e)}")
        # 빈 라우터 생성 - 기본 응답
        empty_router = APIRouter()
        
        @empty_router.get("/")
        async def empty_response():
            return {"error": f"이 기능은 현재 사용할 수 없습니다. ({config['module']} 로드 실패)"}
            
        app.include_router(empty_router, prefix=config["prefix"])

# 기본 라우트
@app.get("/")
async def root():
    return {"message": "API is running"}
