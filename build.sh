#!/bin/bash
set -e

# 시스템 의존성 설치
apt-get update
apt-get install -y build-essential libssl-dev libasound2-dev ffmpeg libsndfile1 python3-dev

# Python 의존성 설치
pip install --upgrade pip==24.0
pip install wheel setuptools

# 일부 문제가 될 수 있는 패키지 먼저 설치
pip install --no-deps PyYAML==6.0
pip install --no-deps omegaconf==2.0.5
pip install --no-deps hydra-core==1.0.7

# 나머지 패키지 설치
pip install -r requirements.txt --no-deps
pip install -r requirements.txt 