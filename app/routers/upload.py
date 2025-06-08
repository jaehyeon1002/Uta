from fastapi import APIRouter, UploadFile, File, Depends, Header
from pydantic import BaseModel
import shutil
import os
from app.utils import get_current_user

router = APIRouter()

UPLOAD_DIR = "uploads"  # 기본 저장 경로

class UploadResponse(BaseModel):
    message: str
    filename: str
    path: str

@router.post("/file", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user)
):
    # 사용자별 업로드 디렉토리 설정
    user_upload_dir = os.path.join("user_data", user_id, "uploads")
    if not os.path.exists(user_upload_dir):
        os.makedirs(user_upload_dir)

    save_path = os.path.join(user_upload_dir, file.filename)

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "message": "파일 업로드 및 저장 성공",
        "filename": file.filename,
        "path": save_path
    }
