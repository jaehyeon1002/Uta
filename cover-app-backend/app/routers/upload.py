from fastapi import APIRouter, UploadFile, File, Depends, Header
from pydantic import BaseModel
import shutil
import os
from app.utils import get_current_user
import uuid

router = APIRouter()

UPLOAD_DIR = "uploads"  # 기본 저장 경로

# 업로드 디렉토리 생성
os.makedirs(UPLOAD_DIR, exist_ok=True)

class UploadResponse(BaseModel):
    message: str
    filename: str
    path: str
    url: str  # 웹에서 접근 가능한 URL 추가

@router.post("/file", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user)
):
    # 파일 확장자 가져오기
    file_ext = os.path.splitext(file.filename)[1]
    # 고유한 파일명 생성
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    
    # 파일을 uploads 디렉토리에 저장 (웹에서 접근 가능하도록)
    save_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 웹에서 접근 가능한 URL 생성
    file_url = f"/uploads/{unique_filename}"
    
    # 사용자별 디렉토리에도 복사 (선택사항)
    user_upload_dir = os.path.join("user_data", user_id, "uploads")
    if not os.path.exists(user_upload_dir):
        os.makedirs(user_upload_dir)
    
    user_save_path = os.path.join(user_upload_dir, unique_filename)
    shutil.copy2(save_path, user_save_path)

    return {
        "message": "파일 업로드 및 저장 성공",
        "filename": file.filename,
        "path": save_path,
        "url": file_url  # 웹에서 접근 가능한 URL 반환
    }