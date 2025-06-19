from fastapi import APIRouter, UploadFile, File, Depends, Header, Request
from pydantic import BaseModel
import shutil
import os
from typing import Optional
from app.utils import get_current_user
import uuid
import logging

router = APIRouter()

UPLOAD_DIR = "uploads"  # 기본 저장 경로

# 업로드 디렉토리 생성
os.makedirs(UPLOAD_DIR, exist_ok=True)

logger = logging.getLogger(__name__)

class UploadResponse(BaseModel):
    message: str
    filename: str
    path: str
    url: str  # 웹에서 접근 가능한 URL 추가

@router.post("/file", response_model=UploadResponse)
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(None)
):
    # --- 시작 로그 --------------------------------------
    logger.info(f"[Upload] ▶ 요청 수신: filename={file.filename}, content_type={file.content_type}")

    # 인증 토큰 파싱(있으면)
    if authorization and authorization.startswith("Bearer "):
        try:
            user_id = get_current_user(authorization)
        except Exception:
            user_id = "anonymous"
    else:
        user_id = "anonymous"
    
    # 파일 확장자 가져오기
    file_ext = os.path.splitext(file.filename)[1]
    # 고유한 파일명 생성
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    
    # 파일을 uploads 디렉토리에 저장 (웹에서 접근 가능하도록)
    save_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    try:
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.exception("[Upload] 파일 저장 중 오류")
        raise
    
    # 웹에서 접근 가능한 URL 생성
    file_url = f"/uploads/{unique_filename}"
    
    # 사용자별 디렉토리에도 복사 (선택사항)
    user_upload_dir = os.path.join("user_data", user_id, "uploads")
    if not os.path.exists(user_upload_dir):
        os.makedirs(user_upload_dir)
    
    user_save_path = os.path.join(user_upload_dir, unique_filename)
    shutil.copy2(save_path, user_save_path)

    logger.info(f"[Upload] ✔ 저장 완료: {save_path}")

    return {
        "message": "파일 업로드 및 저장 성공",
        "filename": file.filename,
        "path": save_path,
        "url": file_url  # 웹에서 접근 가능한 URL 반환
    }
