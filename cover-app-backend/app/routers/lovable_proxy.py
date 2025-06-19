from fastapi import APIRouter, HTTPException
import os
import httpx

router = APIRouter()

# 환경 변수에서 Lovable 프로젝트 ID와(선택) API Key를 읽어옵니다.
PROJECT_ID = os.getenv("LOVABLE_PROJECT_ID")
API_KEY = os.getenv("LOVABLE_API_KEY")
LOVABLE_BASE = "https://lovable-api.com"

if not PROJECT_ID:
    # 애플리케이션 부팅 시 경고용 로그
    import logging
    logging.getLogger(__name__).warning("LOVABLE_PROJECT_ID 환경변수가 설정되지 않았습니다. /lovable 엔드포인트는 500을 반환합니다.")

@router.get("/latest-message")
async def get_latest_message():
    """Lovable API 의 latest-message 엔드포인트를 서버 측에서 프록시합니다."""
    if not PROJECT_ID:
        raise HTTPException(status_code=500, detail="LOVABLE_PROJECT_ID not configured")

    url = f"{LOVABLE_BASE}/projects/{PROJECT_ID}/latest-message"
    headers = {"User-Agent": "cover-app-backend/1.0"}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers, timeout=10)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Lovable upstream error: {e}")

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    # 동일한 JSON 그대로 반환
    return resp.json() 