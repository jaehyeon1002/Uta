import os
import logging
from pathlib import Path
from typing import Optional, Dict
from app.utils.audio_validator import AudioValidator
import numpy as np

logger = logging.getLogger(__name__)

class TrainerService:
    # 학습 관련 상수
    MIN_TOTAL_DURATION = 300  # 최소 총 음성 길이 (초)
    MIN_SAMPLES = 10  # 최소 필요 샘플 수
    MAX_SAMPLES = 50  # 최대 허용 샘플 수
    
    def __init__(self, base_dir: str = "user_data"):
        self.base_dir = Path(base_dir)
        self.validator = AudioValidator()
        
    def check_training_requirements(self, user_id: str) -> bool:
        """학습 요구사항 확인"""
        try:
            samples_dir = self.base_dir / user_id / "samples"
            if not samples_dir.exists():
                return False
                
            # 샘플 수 확인
            samples = list(samples_dir.glob("*.wav"))
            if len(samples) < self.MIN_SAMPLES:
                logger.warning(f"샘플 수가 부족합니다. 현재: {len(samples)}, 필요: {self.MIN_SAMPLES}")
                return False
                
            # 총 음성 길이 확인
            total_duration = sum(self.validator.get_duration(str(sample)) for sample in samples)
            if total_duration < self.MIN_TOTAL_DURATION:
                logger.warning(f"총 음성 길이가 부족합니다. 현재: {total_duration}초, 필요: {self.MIN_TOTAL_DURATION}초")
                return False
                
            # 음성 다양성 확인
            if not self._has_sufficient_variety(samples):
                logger.warning("음성의 다양성이 부족합니다")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"학습 요구사항 확인 실패: {str(e)}")
            return False
            
    def train_user_voice(self, user_id: str) -> Dict:
        """사용자 음성 모델 학습"""
        try:
            # 학습 요구사항 확인
            if not self.check_training_requirements(user_id):
                raise ValueError("학습 요구사항을 충족하지 못했습니다")
                
            # 학습 진행
            logger.info(f"사용자 {user_id}의 음성 모델 학습 시작")
            
            # TODO: 실제 학습 로직 구현
            # 현재는 더미 응답 반환
            return {
                "status": "success",
                "message": "학습이 완료되었습니다",
                "user_id": user_id,
                "model_id": f"model_{user_id}",
                "estimated_time": "약 30분"
            }
            
        except Exception as e:
            logger.error(f"학습 실패: {str(e)}")
            raise
            
    def get_training_status(self, user_id: str) -> Dict:
        """학습 상태 조회"""
        try:
            samples_dir = self.base_dir / user_id / "samples"
            if not samples_dir.exists():
                return {
                    "status": "no_samples",
                    "message": "샘플이 없습니다",
                    "samples_count": 0,
                    "total_duration": 0
                }
                
            samples = list(samples_dir.glob("*.wav"))
            total_duration = sum(self.validator.get_duration(str(sample)) for sample in samples)
            
            return {
                "status": "ready" if self.check_training_requirements(user_id) else "insufficient",
                "message": "학습 가능" if self.check_training_requirements(user_id) else "학습 요구사항 미달",
                "samples_count": len(samples),
                "total_duration": total_duration,
                "requirements": {
                    "min_samples": self.MIN_SAMPLES,
                    "min_duration": self.MIN_TOTAL_DURATION
                }
            }
            
        except Exception as e:
            logger.error(f"학습 상태 조회 실패: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
            
    def _has_sufficient_variety(self, samples: list) -> bool:
        """음성 다양성 확인"""
        try:
            # 샘플 길이의 표준편차 계산
            durations = [self.validator.get_duration(str(sample)) for sample in samples]
            std_dev = np.std(durations)
            
            # 표준편차가 충분히 크면 다양성이 있다고 판단
            return std_dev > np.mean(durations) * 0.3
            
        except Exception as e:
            logger.error(f"음성 다양성 확인 실패: {str(e)}")
            return False 