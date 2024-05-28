import os
from starlette.config import Config

# Heroku 환경 변수 사용 여부를 확인하는 플래그
is_heroku = os.getenv("ENV") == "HEROKU"

if is_heroku:
    # Heroku 환경 변수 직접 사용
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_API = os.getenv("SUPABASE_API")
    POST_API_KEY = os.getenv("POST_API_KEY")
    POST_BASE_URL = os.getenv("POST_BASE_URL")
    IMAGE_BASE_URL = os.getenv("IMAGE_BASE_URL")
else:
    # .env 파일 로드
    _config = Config(".env")

    # 환경 변수 설정
    SUPABASE_URL = _config("SUPABASE_URL")
    SUPABASE_API = _config("SUPABASE_API")
    POST_API_KEY = _config("POST_API_KEY")
    POST_BASE_URL = _config("POST_BASE_URL")
    IMAGE_BASE_URL = _config("IMAGE_BASE_URL")
