from fastapi import HTTPException, APIRouter
from pydantic import BaseModel

from role_db import update_users


prefer_genres_router = APIRouter()




class PreferGenres(BaseModel):
    id: str
    genres: list


@prefer_genres_router.post("/prefer-genres")
async def get_movie_detail(item: PreferGenres):
    try:
        res = update_users(item.id, item.genres)
        
        return {"res": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
