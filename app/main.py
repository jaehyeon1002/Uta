from fastapi import FastAPI, APIRouter, Form, Body
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
import importlib.util
import logging
import sys
from pathlib import Path

# 로거 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 현재 디렉토리 구조 탐색
current_file = Path(__file__).resolve()
current_dir = current_file.parent
project_root = current_dir.parent

logger.info(f"현재 파일 경로: {current_file}")
logger.info(f"현재 디렉토리: {current_dir}")
logger.info(f"프로젝트 루트: {project_root}")

# 가능한 라우터 디렉토리 경로
possible_router_dirs = [
    current_dir / "routers",  # app/routers
    project_root / "app" / "routers",  # /project_root/app/routers
    project_root / "routers",  # /project_root/routers
]

routers_dir = None
for path in possible_router_dirs:
    if path.exists() and path.is_dir():
        routers_dir = path
        logger.info(f"라우터 디렉토리 발견: {routers_dir}")
        break

if not routers_dir:
    logger.error("라우터 디렉토리를 찾을 수 없습니다!")
    # 대체 경로 시도
    routers_dir = current_dir / "routers"
    logger.info(f"대체 라우터 디렉토리 사용: {routers_dir}")

# 디렉토리 내용 출력
if routers_dir and routers_dir.exists():
    logger.info(f"{routers_dir} 디렉토리 내용:")
    for item in routers_dir.iterdir():
        logger.info(f"  - {item.name}")
else:
    logger.error(f"{routers_dir} 디렉토리가 존재하지 않습니다.")
    
sys.path.insert(0, str(project_root))

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
        "*",  # 개발 중에는 모든 출처 허용
    ],
    allow_credentials=True,
    allow_methods=["*"],  # 모든 메소드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

# 기본 라우트
@app.get("/")
async def root():
    return {"message": "API is running"}

# URL 요청 모델 정의
class URLRequest(BaseModel):
    url: str

# YouTube 다운로드 엔드포인트 직접 구현 - 여러 입력 형식 지원
@app.post("/upload/url")
async def upload_url(
    url_data: URLRequest = Body(None),
    url: str = Form(None)
):
    try:
        # 다양한 입력 방식 처리
        final_url = None
        if url_data and url_data.url:
            final_url = url_data.url
            logger.info(f"JSON 본문에서 URL 추출: {final_url}")
        elif url:
            final_url = url
            logger.info(f"폼 데이터에서 URL 추출: {final_url}")
        else:
            logger.error("URL을 찾을 수 없습니다")
            return {"error": "URL을 제공해주세요"}
            
        # 로그 출력
        logger.info(f"URL 다운로드 요청: {final_url}")
        
        import yt_dlp
        import uuid
        
        # 다운로드 디렉토리 생성
        download_dir = "downloads"
        os.makedirs(download_dir, exist_ok=True)
        
        # 고유한 파일명 생성
        file_id = str(uuid.uuid4())
        output_template = os.path.join(download_dir, f"{file_id}.%(ext)s")
        
        # YouTube API 키 가져오기
        youtube_api_key = os.getenv("YOUTUBE_API_KEY", "")
        
        # 다운로드 옵션 설정
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_template,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': False,
            'verbose': True,
        }
        
        # API 키 설정
        if youtube_api_key:
            ydl_opts['ap_mso'] = youtube_api_key
            logger.info("YouTube API 키가 설정되었습니다.")
        else:
            logger.warning("YouTube API 키가 설정되지 않았습니다.")
        
        # 다운로드 실행
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info(f"다운로드 시작: {final_url}")
            ydl.download([final_url])
        
        # 결과 파일 경로
        output_path = os.path.join(download_dir, f"{file_id}.mp3")
        
        if os.path.exists(output_path):
            logger.info(f"다운로드 성공: {output_path}")
            return {"message": "다운로드 성공", "file_path": output_path}
        else:
            logger.error("다운로드된 파일을 찾을 수 없습니다")
            return {"error": "다운로드된 파일을 찾을 수 없습니다"}
            
    except Exception as e:
        logger.error(f"다운로드 실패: {str(e)}")
        return {"error": f"YouTube URL 다운로드 중 오류 발생: {str(e)}"}

# 동적으로 라우터 모듈 로드하는 함수
def load_router_from_file(file_path, router_name="router"):
    try:
        module_name = file_path.stem
        logger.info(f"모듈 로드 시도: {module_name} (파일: {file_path})")
        
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None:
            logger.error(f"모듈 스펙을 찾을 수 없음: {file_path}")
            return None
            
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        router = getattr(module, router_name, None)
        if router is None:
            logger.error(f"라우터를 찾을 수 없음: {router_name} in {module_name}")
            return None
            
        logger.info(f"라우터 로드 성공: {module_name}")
        return router
    except Exception as e:
        logger.error(f"라우터 로드 실패: {file_path} - {str(e)}")
        return None

# routers_dir이 존재하는 경우에만 라우터 로드 시도
if routers_dir and routers_dir.exists():
    # 각 라우터 파일을 직접 검색하여 로드
    router_config = [
        {"file": "auth.py", "prefix": "/auth"},
        {"file": "upload.py", "prefix": "/upload"},
        {"file": "convert.py", "prefix": "/convert"},
        {"file": "split.py", "prefix": "/audio"},
        {"file": "convert_svc.py", "prefix": "/svc"},
        {"file": "train.py", "prefix": "/train"}
    ]

    for config in router_config:
        file_path = routers_dir / config["file"]
        if file_path.exists():
            logger.info(f"라우터 파일 발견: {file_path}")
            router = load_router_from_file(file_path)
            if router:
                app.include_router(router, prefix=config["prefix"])
        else:
            logger.error(f"라우터 파일을 찾을 수 없음: {file_path}")
else:
    logger.warning("라우터 디렉토리가 없어 라우터를 로드하지 않습니다.")
