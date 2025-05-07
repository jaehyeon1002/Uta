import os
import subprocess
import uuid

DEMUC_OUTPUT_DIR = "demucs_output"

def separate_audio(input_path: str) -> dict:
    if not os.path.exists(DEMUC_OUTPUT_DIR):
        os.makedirs(DEMUC_OUTPUT_DIR)

    session_id = str(uuid.uuid4())[:8]
    output_dir = os.path.join(DEMUC_OUTPUT_DIR, session_id)

    # demucs 명령어 실행
    try:
        result = subprocess.run([
            "demucs", "-o", output_dir, input_path
        ], capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"Demucs failed: {result.stderr}")

        # 분리된 폴더 구조: demucs_output/<session_id>/htdemucs/<파일명>/
        song_name = os.path.splitext(os.path.basename(input_path))[0]
        
        # demucs 버전에 따라 폴더 구조가 다를 수 있음
        possible_prefix = ["htdemucs", "demucs"]
        stem_dir = None
        
        for prefix in possible_prefix:
            temp_dir = os.path.join(output_dir, prefix, song_name)
            if os.path.exists(temp_dir):
                stem_dir = temp_dir
                break
                
        if stem_dir is None:
            raise FileNotFoundError(f"분리된 파일을 찾을 수 없습니다. 디렉토리: {output_dir}")
        
        # 파일 이름 형식 확인
        vocals_path = os.path.join(stem_dir, "vocals.wav")
        
        # 반주 파일 찾기 (버전에 따라 다름)
        possible_names = ["no_vocals.wav", "other.wav", "accompaniment.wav", "no_other.wav"]
        other_path = None
        
        for name in possible_names:
            temp_path = os.path.join(stem_dir, name)
            if os.path.exists(temp_path):
                other_path = temp_path
                break
        
        if other_path is None:
            other_path = os.path.join(stem_dir, "no_vocals.wav")  # 기본값

        return {
            "vocals": vocals_path,
            "accompaniment": other_path
        }
    except Exception as e:
        raise e