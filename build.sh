#!/bin/bash
set -e

# Python 의존성 설치
pip install --upgrade pip==24.0
pip install wheel setuptools

# 일부 문제가 될 수 있는 패키지 먼저 설치
pip install PyYAML==6.0
pip install omegaconf==2.0.5
pip install hydra-core==1.0.7

# fairseq 의존성 설치
pip install regex sacrebleu bitarray

# 나머지 패키지 설치 - 문제되는 패키지 제외
grep -v "fairseq" requirements.txt | grep -v "pip" > temp_requirements.txt
pip install -r temp_requirements.txt

# fairseq 수동 설치 시도
pip install fairseq==0.10.2 
