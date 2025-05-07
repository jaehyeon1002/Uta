from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
import shutil
import os

router = APIRouter()

UPLOAD_DIR = "uploads"  # 저장 경로

class UploadResponse(BaseModel):
    message: str
    filename: str
    path: str

@router.post("/file", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    save_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "message": "파일 업로드 및 저장 성공",
        "filename": file.filename,
        "path": save_path
    }