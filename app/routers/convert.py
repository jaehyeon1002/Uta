from fastapi import APIRouter, Form
from pydantic import BaseModel
from app.services.downloader import download_audio_from_url
import os

router = APIRouter()

class UploadResponse(BaseModel):
    message: str
    filename: str
    path: str

@router.post("/url", response_model=UploadResponse)
async def upload_url(url: str = Form(...)):
    saved_path = download_audio_from_url(url)
    filename = os.path.basename(saved_path)

    return {
        "message": "URL 음원 다운로드 성공",
        "filename": filename,
        "path": saved_path
    }