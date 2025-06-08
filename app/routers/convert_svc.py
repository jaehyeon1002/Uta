from fastapi import APIRouter, Form, Depends
from pydantic import BaseModel
from app.services.svc import convert_vocals_with_svc
from app.utils import get_current_user
import os

router = APIRouter()

class ConvertResponse(BaseModel):
    message: str
    output_path: str

@router.post("/voice-convert", response_model=ConvertResponse)
async def voice_convert(
    path: str = Form(...), 
    user_id: str = Depends(get_current_user)
):
    if not os.path.exists(path):
        return {"message": "입력 파일 없음", "output_path": ""}

    try:
        converted = convert_vocals_with_svc(path, user_id)
        return {
            "message": "변환 성공",
            "output_path": converted
        }
    except Exception as e:
        return {"message": f"에러: {str(e)}", "output_path": ""}
