# 이 파일은 app.utils 디렉토리를 파이썬 패키지로 인식하게 합니다.
import os

# YouTube API 키 설정
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")  # 환경 변수에서 가져오기

"""
app.utils 패키지 초기화

패키지와 동일한 이름의 모듈(utils.py) 가 동시에 존재해 import 충돌이 발생하므로,
필요한 상수/함수를 직접 재정의하여 외부 라우터에서 `from app.utils import ...` 가
정상 동작하도록 합니다.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import HTTPException, Header

# ------------------------------------------------------------
# 공통 상수 / 환경변수
# ------------------------------------------------------------

LOG_DIR = "logs"

# JWT 설정
SECRET_KEY = os.getenv("SECRET_KEY", "YOUR_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7일

# ------------------------------------------------------------
# 유틸리티 함수 (로그/토큰/인증)
# ------------------------------------------------------------


def setup_logger(name: str, log_level: int = logging.INFO):
    """애플리케이션 전역 로거를 반환합니다."""
    # 로그 디렉토리 생성
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)

        current_date = datetime.now().strftime('%Y-%m-%d')
        log_file = os.path.join(LOG_DIR, f"{name}_{current_date}.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

    return logger


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """JWT 액세스 토큰을 생성합니다."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str):
    """JWT 토큰을 검증하고 user_id 를 추출합니다."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="유효하지 않은 토큰")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="인증 실패")


def get_current_user(authorization: str = Header(None)):
    """FastAPI Depends 용 현재 사용자 식별 함수"""
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="인증 헤더가 없거나 잘못됨")

    token = authorization.split("Bearer ")[1]
    return verify_token(token)


# ------------------------------------------------------------
# 기타 유틸 함수 (경로 등) – 기존 utils.py 코드 그대로 이동
# ------------------------------------------------------------


def get_absolute_path(relative_path: str) -> str:
    """상대 경로를 절대 경로로 변환합니다."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, relative_path)


def ensure_dir_exists(directory: str):
    """디렉토리가 존재하지 않으면 생성합니다."""
    if not os.path.exists(directory):
        os.makedirs(directory) 