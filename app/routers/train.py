from fastapi import APIRouter, UploadFile, File, Form
import os
import shutil
from app.services.trainer import train_user_voice

router = APIRouter()

@router.post("/upload-voice")
async def upload_user_voice(user_id: str = Form(...), file: UploadFile = File(...)):
    save_dir = f"user_data/{user_id}/samples"
    os.makedirs(save_dir, exist_ok=True)

    file_path = os.path.join(save_dir, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return {"message": "음성 업로드 완료", "path": file_path}
    
@router.post("/train")
async def train_voice(user_id: str = Form(...)):
    result = train_user_voice(user_id)
    return {"message": result}