import subprocess
import os
import uuid

def convert_vocals_with_svc(input_path: str, user_id: str) -> str:
    # 출력 디렉토리 생성
    os.makedirs("converted", exist_ok=True)
    session_id = str(uuid.uuid4())[:8]
    output_path = f"converted/converted_{session_id}.wav"
    
    # 유저 모델 경로 지정
    model_dir = f"user_data/{user_id}/model"
    
    # SVC 모델 실행 명령어
    command = [
        "python", "so-vits-svc/inference_main.py",
        "-m", f"{model_dir}/G_latest.pth",
        "-c", f"{model_dir}/config.json",
        "-n", f"{model_dir}/kmeans.pt",
        "-i", input_path,
        "-s", user_id,  # 화자 이름은 user_id와 동일하게 가정
        "-o", output_path
    ]
    
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"SVC 변환 실패: {result.stderr}")
    
    return output_path