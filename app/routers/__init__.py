# 이 파일은 app.routers 디렉토리를 파이썬 패키지로 인식하게 합니다. 

# 모든 라우터 모듈을 명시적으로 가져옵니다
from .auth import router as auth
from .upload import router as upload
from .convert import router as convert
from .convert_svc import router as convert_svc
from .split import router as split
from .train import router as train 
