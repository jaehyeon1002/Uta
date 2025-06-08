from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import os
import importlib
import logging
import sys
from pathlib import Path

# 프로젝트 루트 경로를 Python 경로에 추가
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
sys.path.insert(0, str(project_root))

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

# YouTube 다운로드 엔드포인트 직접 구현
@app.post("/upload/url")
async def upload_url(url: str):
    try:
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
            logger.info(f"다운로드 시작: {url}")
            ydl.download([url])
        
        # 결과 파일 경로
        output_path = os.path.join(download_dir, f"{file_id}.mp3")
        
        if os.path.exists(output_path):
            logger.info(f"다운로드 성공: {output_path}")
            return {"message": "다운로드 성공", "file_path": output_path}
        else:
            return {"error": "다운로드된 파일을 찾을 수 없습니다"}
            
    except Exception as e:
        logger.error(f"다운로드 실패: {str(e)}")
        return {"error": f"YouTube URL 다운로드 중 오류 발생: {str(e)}"}

# 각 라우터 로드 시도
try:
    # auth 라우터 로드 시도
    from app.routers.auth import router as auth_router
    app.include_router(auth_router, prefix="/auth")
    logger.info("Auth 라우터 로드 성공")
except Exception as e:
    logger.error(f"Auth 라우터 로드 실패: {str(e)}")
    
try:
    # upload 라우터 로드 시도
    from app.routers.upload import router as upload_router
    app.include_router(upload_router, prefix="/upload")
    logger.info("Upload 라우터 로드 성공")
except Exception as e:
    logger.error(f"Upload 라우터 로드 실패: {str(e)}")
    
try:
    # convert 라우터 로드 시도
    from app.routers.convert import router as convert_router
    app.include_router(convert_router, prefix="/convert")
    logger.info("Convert 라우터 로드 성공")
except Exception as e:
    logger.error(f"Convert 라우터 로드 실패: {str(e)}")
    
try:
    # split 라우터 로드 시도
    from app.routers.split import router as split_router
    app.include_router(split_router, prefix="/audio")
    logger.info("Split 라우터 로드 성공")
except Exception as e:
    logger.error(f"Split 라우터 로드 실패: {str(e)}")
    
try:
    # convert_svc 라우터 로드 시도
    from app.routers.convert_svc import router as convert_svc_router
    app.include_router(convert_svc_router, prefix="/svc")
    logger.info("Convert SVC 라우터 로드 성공")
except Exception as e:
    logger.error(f"Convert SVC 라우터 로드 실패: {str(e)}")
    
try:
    # train 라우터 로드 시도
    from app.routers.train import router as train_router
    app.include_router(train_router, prefix="/train")
    logger.info("Train 라우터 로드 성공")
except Exception as e:
    logger.error(f"Train 라우터 로드 실패: {str(e)}")
