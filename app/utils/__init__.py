# 이 파일은 app.utils 디렉토리를 파이썬 패키지로 인식하게 합니다.
import os

# YouTube API 키 설정
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")  # 환경 변수에서 가져오기

# utils.py에서 모든 함수와 변수를 가져옵니다
from ..utils import * 
