import os
import subprocess
import shutil
import logging
from pathlib import Path

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = "user_data"
SVC_DIR = "so-vits-svc"

def train_user_voice(user_id: str):
    user_path = os.path.join(BASE_DIR, user_id)
    sample_dir = os.path.join(SVC_DIR, "dataset_raw", user_id)

    # 1. 샘플 복사
    if not os.path.exists(sample_dir):
        os.makedirs(sample_dir)
    for f in os.listdir(os.path.join(user_path, "samples")):
        shutil.copy(os.path.join(user_path, "samples", f), sample_dir)

    # 2. 리샘플링
    subprocess.run(["python", "resample.py"], cwd=SVC_DIR)

    # 3. config 및 flist 생성
    subprocess.run(["python", "preprocess_flist_config.py"], cwd=SVC_DIR)

    # 4. 특징 추출
    subprocess.run(["python", "preprocess_hubert_f0.py"], cwd=SVC_DIR)

    # 5. 클러스터링
    subprocess.run(["python", "train_cluster.py"], cwd=SVC_DIR)

    # 6. 모델 학습
    subprocess.run([
        "python", "train.py",
        "-c", "configs/44k/config.json",
        "-m", "44k"
    ], cwd=SVC_DIR)

    # 7. 모델 복사
    model_path = os.path.join(SVC_DIR, "logs/44k")
    output_model_path = os.path.join(user_path, "model")
    os.makedirs(output_model_path, exist_ok=True)

    # 가장 최신 모델 파일 찾기
    g_model_files = [f for f in os.listdir(model_path) if f.startswith("G_") and f.endswith(".pth")]
    if g_model_files:
        # 가장 큰 숫자의 모델 파일 선택
        latest_g_model = sorted(g_model_files, key=lambda x: int(x.split('_')[1].split('.')[0]), reverse=True)[0]
        shutil.copy(os.path.join(model_path, latest_g_model), os.path.join(output_model_path, "G_latest.pth"))
    else:
        # 파일이 없으면 기본 이름으로 시도
        shutil.copy(os.path.join(model_path, "G_40000.pth"), os.path.join(output_model_path, "G_latest.pth"))
        
    shutil.copy(os.path.join(model_path, "config.json"), output_model_path)
    shutil.copy(os.path.join(model_path, "kmeans.pt"), output_model_path)

    return "학습 완료"