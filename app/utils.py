import logging
import os
from datetime import datetime

LOG_DIR = "logs"

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