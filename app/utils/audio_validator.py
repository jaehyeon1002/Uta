import librosa
import numpy as np
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

class AudioValidator:
    # 품질 기준
    MIN_QUALITY_THRESHOLD = 0.7
    MAX_NOISE_THRESHOLD = 0.3
    MIN_VOICE_SEGMENTS = 3
    
    def validate_format(self, filepath: str) -> bool:
        """오디오 파일 형식 검증"""
        try:
            # librosa로 파일 로드 시도
            y, sr = librosa.load(filepath, sr=None)
            return True
        except Exception as e:
            logger.error(f"오디오 형식 검증 실패: {filepath}, 에러: {str(e)}")
            raise ValueError("지원하지 않는 오디오 형식입니다")
            
    def get_duration(self, filepath: str) -> float:
        """오디오 파일 길이 반환 (초)"""
        try:
            y, sr = librosa.load(filepath, sr=None)
            return librosa.get_duration(y=y, sr=sr)
        except Exception as e:
            logger.error(f"오디오 길이 측정 실패: {filepath}, 에러: {str(e)}")
            raise ValueError("오디오 길이를 측정할 수 없습니다")
            
    def validate_quality(self, filepath: str) -> float:
        """오디오 품질 검증 및 점수 반환 (0-1)"""
        try:
            y, sr = librosa.load(filepath, sr=None)
            
            # 노이즈 레벨 계산
            noise_level = self._calculate_noise_level(y)
            if noise_level > self.MAX_NOISE_THRESHOLD:
                raise ValueError("노이즈 레벨이 너무 높습니다")
                
            # 음성 강도 계산
            voice_strength = self._calculate_voice_strength(y)
            
            # 음성 명확도 계산
            clarity = self._calculate_clarity(y, sr)
            
            # 최종 품질 점수 계산
            quality_score = (voice_strength + clarity) / 2
            return quality_score
            
        except Exception as e:
            logger.error(f"오디오 품질 검증 실패: {filepath}, 에러: {str(e)}")
            raise ValueError("오디오 품질을 검증할 수 없습니다")
            
    def validate_audio_content(self, filepath: str):
        """오디오 내용 검증"""
        try:
            y, sr = librosa.load(filepath, sr=None)
            
            # 음성 구간 검출
            voice_segments = self._detect_voice_segments(y, sr)
            if len(voice_segments) < self.MIN_VOICE_SEGMENTS:
                raise ValueError("충분한 음성 구간이 없습니다")
                
            # 음성 다양성 검증
            if not self._has_sufficient_variety(voice_segments):
                raise ValueError("음성의 다양성이 부족합니다")
                
        except Exception as e:
            logger.error(f"오디오 내용 검증 실패: {filepath}, 에러: {str(e)}")
            raise ValueError("오디오 내용을 검증할 수 없습니다")
            
    def _calculate_noise_level(self, y: np.ndarray) -> float:
        """노이즈 레벨 계산"""
        # 음성 구간 외의 부분을 노이즈로 간주
        voice_segments = self._detect_voice_segments(y, sr=22050)
        noise_segments = self._get_noise_segments(voice_segments, len(y))
        
        if not noise_segments:
            return 0.0
            
        noise_energy = np.mean([np.mean(np.abs(y[start:end])) for start, end in noise_segments])
        return noise_energy
        
    def _calculate_voice_strength(self, y: np.ndarray) -> float:
        """음성 강도 계산"""
        # RMS 에너지 계산
        rms = librosa.feature.rms(y=y)[0]
        return np.mean(rms)
        
    def _calculate_clarity(self, y: np.ndarray, sr: int) -> float:
        """음성 명확도 계산"""
        # 스펙트럼 대비 계산
        spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
        return np.mean(spectral_contrast)
        
    def _detect_voice_segments(self, y: np.ndarray, sr: int) -> List[Tuple[int, int]]:
        """음성 구간 검출"""
        # 음성 활동 검출 (VAD)
        intervals = librosa.effects.split(y, top_db=20)
        return [(start, end) for start, end in intervals]
        
    def _get_noise_segments(self, voice_segments: List[Tuple[int, int]], total_length: int) -> List[Tuple[int, int]]:
        """노이즈 구간 추출"""
        noise_segments = []
        last_end = 0
        
        for start, end in sorted(voice_segments):
            if start > last_end:
                noise_segments.append((last_end, start))
            last_end = end
            
        if last_end < total_length:
            noise_segments.append((last_end, total_length))
            
        return noise_segments
        
    def _has_sufficient_variety(self, voice_segments: List[Tuple[int, int]]) -> bool:
        """음성 다양성 검증"""
        if len(voice_segments) < self.MIN_VOICE_SEGMENTS:
            return False
            
        # 구간 길이의 표준편차 계산
        segment_lengths = [end - start for start, end in voice_segments]
        std_dev = np.std(segment_lengths)
        
        # 표준편차가 충분히 크면 다양성이 있다고 판단
        return std_dev > np.mean(segment_lengths) * 0.3 