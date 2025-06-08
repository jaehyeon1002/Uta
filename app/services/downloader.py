import yt_dlp
import os
import uuid
import logging
from app.utils import YOUTUBE_API_KEY

DOWNLOAD_DIR = "downloads"
logger = logging.getLogger(__name__)

def download_audio_from_url(url: str) -> str:
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    # 고유한 파일명 생성
    file_id = str(uuid.uuid4())
    output_template = os.path.join(DOWNLOAD_DIR, f"{file_id}.%(ext)s")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_template,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': False,  # 디버깅을 위해 출력 활성화
        'verbose': True,  # 더 자세한 로그
    }
    
    # YouTube API 키가 설정되어 있으면 추가
    if YOUTUBE_API_KEY:
        ydl_opts['ap_mso'] = YOUTUBE_API_KEY
        logger.info("YouTube API 키가 설정되었습니다.")
    else:
        logger.warning("YouTube API 키가 설정되지 않았습니다.")
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info(f"다운로드 시작: {url}")
            ydl.download([url])
            
        output_path = os.path.join(DOWNLOAD_DIR, f"{file_id}.mp3")
        if os.path.exists(output_path):
            logger.info(f"다운로드 성공: {output_path}")
            return output_path
        else:
            raise FileNotFoundError(f"다운로드된 파일을 찾을 수 없습니다: {output_path}")
            
    except Exception as e:
        logger.error(f"다운로드 실패: {str(e)}")
        raise Exception(f"YouTube URL 다운로드 중 오류 발생: {str(e)}")
