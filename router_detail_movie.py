from fastapi import HTTPException, APIRouter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

from role_db import get_story
from role_db import get_actors
from role_db import get_directors
from Pre_Movie import get_movie
from Pre_Tag import get_tag
from Pre_Rating import get_rating
from Pre_Post import get_post


detail_router = APIRouter()

def load_data():
    movies_data = get_movie()
    links_data = get_post()
    ratings_data = get_rating()
    user_data = []
    
    if not movies_data or not links_data or not ratings_data:
        raise HTTPException(status_code=404, detail="Data not found")
    
    return movies_data, links_data, ratings_data, user_data

def prepare_dicts(ratings_data, links_data):
    ratings_dict = {item['movieId']: item['rating'] for item in ratings_data}
    links_dict = {item['movieId']: {'URL': item['URL'], 'overview': item.get('overview', '')} for item in links_data}
    
    return ratings_dict, links_dict

def get_movie_by_id(movie_id, movies_data):
    for data in movies_data:
        movieData = data

        if movieData['movieId'] == movie_id:
            return movieData

    return None

def create_tfidf_matrix(movies_data):
    tag_strings = []
    movie_ids = []

    for movie in movies_data:
        tags_data = get_tag(movie['movieId'])
        # if tags_data and isinstance(tags_data, list):
        if tags_data:
            tag_string = ' '.join(tag for tag in tags_data)
            tag_strings.append(tag_string)
            movie_ids.append(str(movie['movieId']))
    
    vectorizer = TfidfVectorizer(stop_words=None, token_pattern=r'\b\w+\b')
    tfidf_matrix = vectorizer.fit_transform(tag_strings)

    return tfidf_matrix, movie_ids

def get_similar_movies(movie_id, tfidf_matrix, movie_ids, k=12):
    knn = NearestNeighbors(n_neighbors=k+1, metric='cosine')
    knn.fit(tfidf_matrix)
    
    movie_idx = movie_ids.index(movie_id)
    distances, indices = knn.kneighbors(tfidf_matrix[movie_idx], n_neighbors=k+1)
    
    similar_movie_indices = indices[0][1:]  # exclude the first movie (itself)
    similar_movies = [movie_ids[i] for i in similar_movie_indices]
    
    return similar_movies

@detail_router.get("/get-movie-detail/{movie_id}")
async def get_movie_detail(movie_id: str):
    try:
        movies_data, links_data, ratings_data, user_data = load_data()

        ratings_dict, links_dict = prepare_dicts(ratings_data, links_data)
        

        movie = get_movie_by_id(movie_id, movies_data)
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        
        tfidf_matrix, movie_ids = create_tfidf_matrix(movies_data)
        similar_movie_ids = get_similar_movies(movie_id, tfidf_matrix, movie_ids)
        
        more_like_this = [
            {
                "title": get_movie_by_id(similar_movie_id, movies_data)['title'],
                "cover_url": links_dict[similar_movie_id]['URL'],
                "scope": ratings_dict.get(similar_movie_id, 5),
                "movie_id": similar_movie_id
            } for similar_movie_id in similar_movie_ids if similar_movie_id in links_dict
        ][:12]

        movie_detail = {
            'cover_url': links_dict[movie_id]['URL'],
            'scope': ratings_dict.get(movie_id, 5),
            'title': movie['title'],
            'genres': movie['genres'],
            'actors': get_actors(movie_id),
            'directors': get_directors(movie_id),
            'description': get_story(movie_id),  # 일단 빈 문자열로 설정
            'more-like-this': more_like_this
        }

        return movie_detail

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
