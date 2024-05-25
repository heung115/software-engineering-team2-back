from starlette.config import Config


_config = Config('.env')

# TMDb API 설정
SUPABASE_URL = _config('SUPABASE_URL')
SUPABASE_API = _config('SUPABASE_API')
POST_API_KEY = _config('POST_API_KEY')
POST_BASE_URL = _config('POST_BASE_URL')
IMAGE_BASE_URL = _config('IMAGE_BASE_URL')