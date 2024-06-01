from fastapi import HTTPException, APIRouter
from pydantic import BaseModel

import threading
from router_movie_list import add_job

from role_db import update_users
from role_db import get_genre

prefer_genres_router = APIRouter()


class PreferGenres(BaseModel):
    id: str
    genres: list


@prefer_genres_router.post("/prefer-genres")
def get_movie_detail(item: PreferGenres):
    try:
        genres = ['recommend'] + get_genre()[:-1] 
        add_job(item.id, genres)

        res = update_users(item.id, item.genres)
        
        return {"res": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
