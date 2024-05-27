from fastapi import APIRouter
from role_db import get_genre


genre_router = APIRouter()


@genre_router.get("/genre")
async def get_Allgenre():
  response = get_genre()

  return { "genre": response}