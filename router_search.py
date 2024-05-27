from fastapi import HTTPException, APIRouter
from pydantic import BaseModel

from role_db import get_movie_by_key_word


search_router = APIRouter()




class PreferGenres(BaseModel):
    id: str
    genres: list


@search_router.get("/search/{key_word}")
async def get_movie_detail(key_word: str):
    try:
        res = get_movie_by_key_word(key_word)
        
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
