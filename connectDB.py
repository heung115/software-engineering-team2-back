import os
from supabase import create_client, Client
from starlette.config import Config
from fastapi import APIRouter

router = APIRouter()


def get_supabase():
    # Heroku 환경 변수 사용 여부를 확인하는 플래그
    is_heroku = os.getenv("ENV") == "HEROKU"

    if is_heroku:
        # Heroku 환경 변수 직접 사용
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_API = os.getenv("SUPABASE_API")
    else:
        # .env 파일 로드
        config = Config(".env")
        # 환경 변수 설정
        SUPABASE_URL = config("SUPABASE_URL")
        SUPABASE_API = config("SUPABASE_API")

    if not SUPABASE_URL or not SUPABASE_API:
        raise ValueError("Supabase URL과 API 키가 설정되어야 합니다.")

    supabase: Client = create_client(SUPABASE_URL, SUPABASE_API)
    return supabase
