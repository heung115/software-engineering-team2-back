from fastapi import HTTPException, APIRouter

import random
import time

import threading

from RatingLinkdata import prepare_dicts
from filter_genre_movie import filter_movies_by_genre
from Movie_print import prepare_genre_movies
from UserTags_create import create_user_tags_string
from Cosine_Al_movie import recommend_movies_by_similarity
from All_load_data import load_data

from role_db import check_user_id
from role_db import get_genre
from role_db import get_all_user_id
from role_db import g_get_user_id

# 1차 key : userId, 2차 key : userGenre
pre_recommend_data = {

}

job_queue = []
def make_work_thread():
    thread = threading.Thread(target=refresh_data)
    thread.start()

def add_job(uuid, genres):
    for genre in genres:
        job_queue.append([uuid, genre])

def refresh_data():
    while True:
        if job_queue:
            uuid, genre = job_queue.pop()

            procees_job_sigle_genre(uuid, genre)
    

def process_job(uuid, genres):
    
    if uuid == "no-id":
        for genre in genres:
            res = get_movie_list_no_login(uuid, genre)
            if uuid not in pre_recommend_data:
                pre_recommend_data[uuid] = {}
            pre_recommend_data[uuid][genre] = res
    else:
        for genre in genres:
            res = get_movie_list_with_login(uuid, genre)
            if uuid not in pre_recommend_data:
                pre_recommend_data[uuid] = {}
            pre_recommend_data[uuid][genre] = res


def procees_job_sigle_genre(uuid, genre):
    if uuid == "no-id":
        res = get_movie_list_no_login(uuid, genre)
        if uuid not in pre_recommend_data:
            pre_recommend_data[uuid] = {}
        pre_recommend_data[uuid][genre] = res
    else:
        res = get_movie_list_with_login(uuid, genre)
        if uuid not in pre_recommend_data:
            pre_recommend_data[uuid] = {}
        pre_recommend_data[uuid][genre] = res


def pre_process_user():
    genre = get_genre()[:-1] + ['recommend']
    allUser = get_all_user_id() + ['no-id']
    
    for i in range(0, len(allUser), 8):
        threads = []

        for j in range(i, i + 8):
            if j >= len(allUser):
                continue

            thread = threading.Thread(target=process_job, args=(allUser[j], genre, ))
            threads.append(thread)
            thread.start()
        
        for idx, t in enumerate(threads):
            t.join()
            print(i * 8 + idx, "/", len(allUser), ": clear") 


movie_list_router = APIRouter()

def get_movie_list_no_login(uuid, genre):
    movies_data, links_data, ratings_data, user_data = load_data(uuid)
    ratings_dict, links_dict = prepare_dicts(ratings_data, links_data)

    filtered_movies = None
    if genre not in get_genre():
        filtered_movies = random.sample(movies_data, min(21, len(movies_data)))
    else:
        filtered_movies = filter_movies_by_genre(movies_data, genre)
    
    genre_movies = prepare_genre_movies(filtered_movies[1:], links_dict, ratings_dict)

    recommand = filtered_movies[0]
    recommandId = recommand['movieId']

    return {
        "main": {
            'title': recommand['title'],
            'describe': links_dict[recommandId]['overview'],
            'cover_url': links_dict[recommandId]['URL'],
            'movie_id': recommandId,
        },
        "movies": genre_movies}
    

def get_movie_list_with_login(uuid, genre):
    movies_data, links_data, ratings_data, user_data = load_data(uuid)
    ratings_dict, links_dict = prepare_dicts(ratings_data, links_data)

    if not user_data[0]['UserTags']:
        return get_movie_list_no_login(uuid, genre)

    filtered_movies = None
    if genre not in get_genre():
        filtered_movies = random.sample(movies_data, min(21, len(movies_data)))
    else:
        filtered_movies = filter_movies_by_genre(movies_data, genre)

    genre_movies = prepare_genre_movies(filtered_movies, links_dict, ratings_dict)

    user_tags_string = create_user_tags_string(user_data)
    recommended_movies = recommend_movies_by_similarity(filtered_movies, user_tags_string, links_dict)
    
    
    movie = recommended_movies[0]
    final_recommendations = {
        "title": movie['title'],
        "describe": movie['describe'],
        "cover_url": movie['cover_url'],
        'movie_id': movie['movie_id']
    }

    return {"main": final_recommendations, "movies": genre_movies}


@movie_list_router.get("/get-movie-list/{genre}/{uuid}")
async def recommend_movies(genre: str, uuid: str):
    random.seed(time.time())
    try:
        # id가 DB에 없는 거라면. 에러 없음.
        if not check_user_id(uuid):
            uuid = 'no-id'
        
        if genre not in get_genre():
            genre = 'recommend'
        
        job_queue.append([uuid, genre])
        return pre_recommend_data[uuid][genre]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    