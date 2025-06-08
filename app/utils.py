import logging
import os
from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException, Header
from typing import Optional

LOG_DIR = "logs"

# JWT 설정
SECRET_KEY = os.getenv("SECRET_KEY", "YOUR_SECRET_KEY")  # 환경 변수에서 가져오기
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7일

# YouTube API 키 설정
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")  # 환경 변수에서 가져오기

def setup_logger(name, log_level=logging.INFO):
    """
    애플리케이션 로깅을 설정합니다.
    
    Args:
        name: 로거 이름
        log_level: 로깅 레벨
        
    Returns:
        설정된 로거 객체
    """
    # 로그 디렉토리 생성
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
        
    # 로거 설정
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # 이미 핸들러가 설정되어 있는 경우 추가하지 않음
    if not logger.handlers:
        # 콘솔 핸들러
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)
        
        # 파일 핸들러
        current_date = datetime.now().strftime('%Y-%m-%d')
        log_file = os.path.join(LOG_DIR, f"{name}_{current_date}.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    
    return logger

def get_absolute_path(relative_path):
    """
    상대 경로를 절대 경로로 변환합니다.
    
    Args:
        relative_path: 상대 경로
        
    Returns:
        절대 경로
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, relative_path)

def ensure_dir_exists(directory):
    """
    디렉토리가 존재하는지 확인하고, 없으면 생성합니다.
    
    Args:
        directory: 확인할 디렉토리 경로
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="유효하지 않은 토큰")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="인증 실패")

def get_current_user(authorization: str = Header(None)):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="인증 헤더가 없거나 잘못됨")
    
    token = authorization.split("Bearer ")[1]
    return verify_token(token) 
