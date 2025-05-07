from pathlib import Path
import shutil
import os
from typing import List, Optional
from fastapi import UploadFile
import logging
from app.utils.audio_validator import AudioValidator

logger = logging.getLogger(__name__)

class VoiceSampleService:
    # 샘플 관련 상수
    MIN_SAMPLES = 10  # 최소 필요 샘플 수
    MAX_SAMPLES = 50  # 최대 허용 샘플 수
    AUTO_RETRAIN_THRESHOLD = 5  # 자동 재학습을 위한 새 샘플 수
    
    # 샘플 길이 제한
    MIN_DURATION = 30  # 최소 30초
    MAX_DURATION = 300  # 최대 5분
    RECOMMENDED_DURATION = 180  # 권장 3분
    
    def __init__(self, base_dir: str = "user_data"):
        self.base_dir = Path(base_dir)
        self.validator = AudioValidator()
        
    def get_samples_dir(self, user_id: str) -> Path:
        """사용자의 샘플 디렉토리 경로 반환"""
        return self.base_dir / user_id / "samples"
        
    def save_sample(self, file: UploadFile, user_id: str) -> str:
        """새로운 음성 샘플 저장"""
        samples_dir = self.get_samples_dir(user_id)
        samples_dir.mkdir(parents=True, exist_ok=True)
        
        # 현재 샘플 수 확인
        current_samples = len(list(samples_dir.glob("*.wav")))
        if current_samples >= self.MAX_SAMPLES:
            raise ValueError(f"최대 {self.MAX_SAMPLES}개의 샘플만 저장 가능합니다")
        
        # 임시 파일로 저장
        temp_path = samples_dir / f"temp_{file.filename}"
        try:
            with temp_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # 샘플 검증
            self.validate_sample(str(temp_path))
            
            # 검증 통과 후 최종 저장
            final_path = samples_dir / file.filename
            temp_path.rename(final_path)
            
            return str(final_path)
        except Exception as e:
            if temp_path.exists():
                temp_path.unlink()
            raise e
            
    def validate_sample(self, sample_path: str):
        """샘플 품질 검증"""
        # 기본 오디오 검증
        self.validator.validate_format(sample_path)
        
        # 길이 검증
        duration = self.validator.get_duration(sample_path)
        if duration < self.MIN_DURATION:
            raise ValueError(f"샘플은 최소 {self.MIN_DURATION}초 이상이어야 합니다")
        if duration > self.MAX_DURATION:
            raise ValueError(f"샘플은 {self.MAX_DURATION}초 이하여야 합니다")
        
        # 품질 검증
        quality = self.validator.validate_quality(sample_path)
        if quality < self.validator.MIN_QUALITY_THRESHOLD:
            raise ValueError("샘플 품질이 기준에 미달합니다")
            
        # 음성 내용 검증
        self.validator.validate_audio_content(sample_path)
        
    def list_samples(self, user_id: str) -> List[dict]:
        """사용자의 모든 샘플 목록 반환"""
        samples_dir = self.get_samples_dir(user_id)
        if not samples_dir.exists():
            return []
            
        samples = []
        for file_path in samples_dir.glob("*.wav"):
            try:
                duration = self.validator.get_duration(str(file_path))
                quality = self.validator.validate_quality(str(file_path))
                samples.append({
                    "filename": file_path.name,
                    "path": str(file_path),
                    "duration": duration,
                    "quality": quality,
                    "created_at": file_path.stat().st_mtime
                })
            except Exception as e:
                logger.error(f"샘플 정보 조회 실패: {file_path}, 에러: {str(e)}")
                
        return sorted(samples, key=lambda x: x["created_at"], reverse=True)
        
    def delete_sample(self, sample_id: str) -> bool:
        """특정 샘플 삭제"""
        try:
            sample_path = Path(sample_id)
            if sample_path.exists():
                sample_path.unlink()
                return True
            return False
        except Exception as e:
            logger.error(f"샘플 삭제 실패: {sample_id}, 에러: {str(e)}")
            return False
            
    def get_recording_guidelines(self) -> dict:
        """녹음 가이드라인 제공"""
        return {
            "recommended_duration": "3분",
            "content_suggestions": [
                "다양한 톤과 감정으로 이야기하기",
                "일상적인 대화 내용 녹음",
                "노래나 시 낭송 포함",
                "다양한 발음과 억양 포함"
            ],
            "recording_tips": [
                "조용한 환경에서 녹음",
                "마이크와 적절한 거리 유지",
                "자연스러운 목소리로 녹음",
                "충분한 휴식 후 녹음"
            ]
        } 