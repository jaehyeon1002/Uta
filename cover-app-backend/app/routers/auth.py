from fastapi import APIRouter, HTTPException, Depends, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
import os
import json
import uuid
from app.utils import create_access_token, get_current_user

router = APIRouter()

# 사용자 데이터 저장 경로
USERS_FILE = "user_data/users.json"
os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)

# 사용자 데이터 모델
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str

# 사용자 데이터 파일 로드
def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump({}, f)
        return {}
    
    with open(USERS_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

# 사용자 데이터 저장
def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

# 회원가입 라우트
@router.post("/register", response_model=TokenResponse)
async def register(user: UserCreate):
    users = load_users()
    
    # 이메일 중복 확인
    for existing_user in users.values():
        if existing_user["email"] == user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 등록된 이메일입니다."
            )
    
    # 새 사용자 ID 생성
    user_id = str(uuid.uuid4())
    
    # 사용자 폴더 생성
    os.makedirs(f"user_data/{user_id}", exist_ok=True)
    os.makedirs(f"user_data/{user_id}/model", exist_ok=True)
    
    # 사용자 데이터 저장
    users[user_id] = {
        "id": user_id,
        "username": user.username,
        "email": user.email,
        "password": user.password,  # 실제로는 비밀번호 해싱 필요
    }
    save_users(users)
    
    # 토큰 생성
    access_token = create_access_token(data={"user_id": user_id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user_id
    }

# 로그인 라우트
@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    users = load_users()
    
    # 이메일로 사용자 찾기
    user_id = None
    user = None
    
    for id, data in users.items():
        if data["email"] == user_data.email:
            user_id = id
            user = data
            break
    
    if not user or user["password"] != user_data.password:  # 실제로는 비밀번호 해싱 확인 필요
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다."
        )
    
    # 토큰 생성
    access_token = create_access_token(data={"user_id": user_id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user_id
    }

# 현재 사용자 정보 가져오기
@router.get("/me")
async def get_me(user_id: str = Depends(get_current_user)):
    users = load_users()
    if user_id not in users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    
    user = users[user_id].copy()
    # 비밀번호는 제외하고 반환
    user.pop("password", None)
    return user 