import yt_dlp
import os
import uuid
import logging
from app.utils import YOUTUBE_API_KEY

DOWNLOAD_DIR = "downloads"
logger = logging.getLogger(__name__)

# 환경 변수 기반 프록시 설정 (예: http://user:pass@host:port)
PROXY_URL = os.getenv("PROXY_URL", "")

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
        # 지오우회 및 프록시 설정
        'geo_bypass': True,
        'geo_bypass_country': 'US',
        'geo_bypass_ip_block': 'US',
    }
    
    # 프록시가 지정되어 있으면 yt-dlp 옵션에 포함
    if PROXY_URL:
        ydl_opts['proxy'] = PROXY_URL
        logger.info(f"프록시 사용: {PROXY_URL}")
    
    # YouTube API 키가 설정되어 있으면 추가
    youtube_api_key = os.getenv("YOUTUBE_API_KEY", "")
    if youtube_api_key:
        ydl_opts['ap_mso'] = youtube_api_key
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
            
    except yt_dlp.utils.GeoRestrictedError as ge:
        logger.error(f"Geo 제한 오류: {str(ge)}")
        raise Exception("지리적 제한으로 인해 다운로드할 수 없는 URL입니다. VPN/프록시를 설정하거나 다른 소스를 이용하세요.")
    except Exception as e:
        logger.error(f"다운로드 실패: {str(e)}")
        raise Exception(f"YouTube URL 다운로드 중 오류 발생: {str(e)}")
