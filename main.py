from fastapi import FastAPI
from router_movie_list import movie_list_router
from router_genre import genre_router
from router_detail_movie import detail_router
from router_save_prefered import prefer_genres_router
from router_search import search_router
from fastapi.middleware.cors import CORSMiddleware
import uvicorn


from preprocess import init_multi_thread
from preprocess import init_user_data


app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://heung115.iptime.org:8008","*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
# async def root():
def root():
    return {"message": "Hello World"}


@app.get("/home")
def home():
    return {"message": "home"}

app.include_router(genre_router)
app.include_router(movie_list_router)
app.include_router(detail_router)
app.include_router(prefer_genres_router)
app.include_router(search_router)

if __name__ == "__main__":
    init_multi_thread()
    init_user_data()
    uvicorn.run(app, host="127.0.0.1", port = 8000)