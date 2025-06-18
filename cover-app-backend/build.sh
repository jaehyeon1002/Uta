#!/bin/bash
set -e

# 기본 도구 설치
pip install --upgrade pip==24.0
pip install setuptools wheel

# 기본 패키지 먼저 설치
pip install fastapi uvicorn python-multipart PyJWT==2.8.0 email-validator==2.1.0

# 문제가 될 수 있는 패키지들을 개별적으로 설치
pip install pyyaml
pip install numpy==1.23.5
pip install scipy==1.10.0
pip install SoundFile==0.12.1
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install torchcrepe
pip install tqdm rich loguru

# 음성 처리 관련 패키지
pip install pydub
pip install ffmpeg-python
pip install yt-dlp
pip install pyworld
pip install scikit-maad
pip install praat-parselmouth
pip install librosa==0.9.1

# 변환 관련 패키지
pip install transformers

mkdir -p downloads uploads converted user_data 