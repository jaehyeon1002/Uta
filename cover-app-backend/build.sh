#!/usr/bin/env bash
set -e

echo "▶ 시스템 패키지 설치 (ffmpeg 등)"
apt-get update -qq
apt-get install -y --no-install-recommends ffmpeg

echo "▶ pip 최신화 & 기본 휠 설치"
pip install --upgrade pip==24.0
pip install setuptools wheel

echo "▶ 경량 requirements.txt 한 번에 설치"
pip install -r requirements.txt

# ── 추가 파이썬 패키지를 따로 설치하고 싶으면 아래에 작성 ──
# 예) pip install some-private-package

echo "▶ 작업 디렉터리 준비"
mkdir -p downloads uploads converted user_data
