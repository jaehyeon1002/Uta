from fastapi import APIRouter, Form
from pydantic import BaseModel
from app.services.splitter import separate_audio
import os

router = APIRouter()

class SplitResponse(BaseModel):
    message: str
    vocals_path: str
    accompaniment_path: str

@router.post("/split", response_model=SplitResponse)
async def split_audio(path: str = Form(...)):
    if not os.path.exists(path):
        return {"message": "파일이 존재하지 않음", "vocals_path": "", "accompaniment_path": ""}

    result = separate_audio(path)
    return {
        "message": "보컬/반주 분리 성공",
        "vocals_path": result["vocals"],
        "accompaniment_path": result["accompaniment"]
    }