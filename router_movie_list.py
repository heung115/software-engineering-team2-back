from fastapi import HTTPException, APIRouter

import random
import time

from RatingLinkdata import prepare_dicts
from filter_genre_movie import filter_movies_by_genre
from Movie_print import prepare_genre_movies
from UserTags_create import create_user_tags_string
from Cosine_Al_movie import recommend_movies_by_similarity
from All_load_data import load_data

from role_db import check_user_id
from role_db import get_genre

movie_list_router = APIRouter()

TEST_USER_ID = "TestID"  # 테스트용 유저 아이디

@movie_list_router.get("/get-movie-list/{genre}/{uuid}")
async def recommend_movies(genre: str, uuid: str):
    random.seed(time.time())
    try:
        # id가 DB에 없는 거라면. 에러 없음.
        if not check_user_id(uuid):
            
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
                "movies": genre_movies
            }


        movies_data, links_data, ratings_data, user_data = load_data(uuid)
        ratings_dict, links_dict = prepare_dicts(ratings_data, links_data)

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

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))