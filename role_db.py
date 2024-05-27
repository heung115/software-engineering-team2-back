from preprocess import g_total_movie_data
from preprocess import init_multi_thread
from preprocess import g_total_user_data
from preprocess import init_user_data
import preprocess as pc


def _check_movie_init():
    """영화 데이터를 보유하고 있지 않다면 초기화를 함.
    """
    if not g_total_movie_data:
        init_multi_thread()


def _check_user_init(userId):
    """모든 사용자 데이터가 초기화 되었는 지 확인.

    Args:
        userId (uuid{String}): 초기화 되었더라고 있어야 하는 사용자 ID
    """
    if not g_total_user_data or userId not in g_total_user_data:
        init_user_data()


def get_genre():
    """모든 영화 장르 정보를 반환.

    Returns:
        String List: 모든 영화 장르 정보.
    """
    _check_movie_init()

    data = {'IMAX', 'Crime', 'Animation', 'Documentary', 'Romance', 'Mystery', 'Children', 'Musical', 'Film-Noir',
            'Fantasy', 'Horror', 'Drama', 'Action', 'Etc', 'Thriller', 'Western', 'Sci-Fi', 'Comedy', 'Adventure',
            'War'}

    for d in g_total_movie_data:
        data |= g_total_movie_data[d][pc.MOVIE_GENRE]

    return sorted(data, key=lambda x: "Z" if x == 'Etc' else x)


def g_get_movie():
    """모든 영화의 [title, movieId, genres]를 반환함.

    Returns:
        Dictionary List: {"title": String, "movieId": String, "genres": List} item list
    """
    _check_movie_init()

    res = []

    for movieId in g_total_movie_data:
        movie_data = g_total_movie_data[movieId]
        data = {
            "title": movie_data[pc.MOVIE_TITLE],
            "movieId": str(movieId),
            "genres": movie_data[pc.MOVIE_GENRE]
        }
        res.append(data)

    return res


def g_get_rating():
    """모든 영화의 평점을 반환

    Returns:
        Dictionary List: {"movieId": Integer, "rating": Float} item list
    """
    _check_movie_init()

    res = []

    for movieId in g_total_movie_data:
        movie_data = g_total_movie_data[movieId]

        data = {
            "movieId": str(movieId),
            "rating": movie_data[pc.MOVIE_SCOPE]
        }

        res.append(data)
    
    return res


def g_get_tag(movie_id):
    """원하는 영화의 태그들을 반환

    Args:
        movie_id (int): 원하는 영화 id

    Returns:
        String List: 해당 영화의 모든 태그
    """
    _check_movie_init()

    res = g_total_movie_data[str(movie_id)][pc.MOVIE_TAGS]

    print("res")

    return res


def g_get_post():
    _check_movie_init()

    res = []
    for movieId in g_total_movie_data:
        movie = g_total_movie_data[movieId]

        res.append({
            "movieId": str(movieId),
            "URL": movie[pc.MOVIE_POSTER],
            "overview": movie[pc.MOVIE_OVERVIEW]
        })

    return res

def get_story(movie_id):
    _check_movie_init()
    return g_total_movie_data[str(movie_id)][pc.MOVIE_STORY]


def get_actors(movie_id):
    _check_movie_init()

    res = []
    actor = g_total_movie_data[str(movie_id)][pc.MOVIE_CAST]

    if actor:
        for cast in actor:
            castData = actor[cast]

            data = {
                'name': cast,
                'profile_url': castData[pc.PROFILE_URL],
                'character': castData[pc.CAST_CHARACTER]
            }

            res.append(data)
    return res


def get_directors(movie_id):
    _check_movie_init()

    res = []
    movie = g_total_movie_data[str(movie_id)][pc.MOVIE_CREW]

    if movie:
        for cast in movie:
            castData = movie[cast]

            data = {
                'name': cast,
                'profile_url': castData[pc.PROFILE_URL],
                'character': castData[pc.CREW_JOB]
            }

            res.append(data)

    return res


def g_get_user_id(user_id):
    """해당 사용자가 선호하는 장르 반환

    Args:
        user_id (uuid{String}): 검색하고자하는 사용자의 id

    Returns:
        Dictionary: {"UserId": uuid, "UserTags": Genre array}
    """
    _check_user_init(user_id)
    
    if user_id in g_total_user_data:
        return {"UserId": user_id,
            "UserTags": g_total_user_data[user_id][pc.USER_TAGS]}
    else:
        return {"UserId": None, "UserTags": None}
    

def check_user_id(uuid):
    _check_user_init(uuid)

    if uuid in g_total_user_data:
        return True
    return False