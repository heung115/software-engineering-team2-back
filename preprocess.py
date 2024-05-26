from connectDB import get_supabase
import random
import requests
import threading
from bs4 import BeautifulSoup as bs
from get_config import POST_API_KEY
from get_config import POST_BASE_URL
from get_config import IMAGE_BASE_URL
import time


# key : movieId, g_total_movie_data[key] = movie_data
g_total_movie_data = {}

# movie_data is dictionary, data format and keys
MOVIE_TITLE = 0  # data type : String
MOVIE_POSTER = 1  # data type : String, URL
MOVIE_GENRE = 2  # data type : String array
MOVIE_TAGS = 3  # data type : String array
MOVIE_SCOPE = 4  # data type : float
MOVIE_OVERVIEW = 5  # data type : String
MOVIE_STORY = 6  # data type : String
MOVIE_CAST = 7  # data type : dictionary or None
MOVIE_CREW = 8  # data type : dictionary or None

# MOVIE_CAST and MOVIE_CREW dictionary data format
# key : actor name or director name, g_total_movie_data[MOVIE_CAST][key] = charactor_data

# charactor_data is dictionary, data format and keys
PROFILE_URL = 9  # data type : String or None
CAST_CHARACTER = 10  # data type : String or None
CREW_JOB = 11  # data type : String or None

# key : userId, g_total_user_data[key] = user_data
g_total_user_data = {}

# user_data is dinctionary, data format and keys
USER_TAGS = 12  # data type : String array or None
USER_STACK = 13  # data type : Integer array or None

# 실제 DB 객체
supabase = get_supabase()


def init_crew_cast(tm_db_id):
    """
    tmdb API 통해서 출연진이랑 연출진 정보를 가져오기.
    따로 DB에 저장하지 않고 서버 실행 시킬 때 마다 API를 통해서 가져오기.

    :param tm_db_id: Links_Table tmdbId
    :return: [cast list, crew list]
    """
    if not tm_db_id:
        return [None, None]

    response = requests.get(
        f"{POST_BASE_URL}/{tm_db_id}/credits", params={"api_key": POST_API_KEY}
    ).json()

    cast = {}
    if "cast" not in response:
        cast = None
        print("none cast :", tm_db_id)
        print("response :", response.keys())
    else:
        for d in response["cast"]:
            imagePath = d["profile_path"]
            cast[d["original_name"]] = {
                "profile_path": (
                    (IMAGE_BASE_URL + d["profile_path"]) if imagePath else None
                ),
                "character": d["character"],
            }

    crew = {}
    if "crew" not in response:
        crew = None
        print("none crew :", tm_db_id)
        print("response :", response.keys())
    else:
        for d in response["crew"]:
            imagePath = d["profile_path"]
            crew[d["original_name"]] = {
                "profile_path": (
                    (IMAGE_BASE_URL + d["profile_path"]) if imagePath else None
                ),
                "job": d["known_for_department"],
            }

    return [cast, crew]


def init_job(data):
    """
    멀티스레드가 수행할 작업. 입력으로 주어지는 영화 데이터를 완성 시킴.

    :param data: 한 영화의 데이터
    :return: None
    """
    # 기본 정보
    movie_id = data["movieId"]
    movie_title = data["title"]
    movie_poster = data["poster_url"]
    movie_overview = data["overview"]
    movie_story = data["story_line"]

    # 현재 영화의 장르 정보
    getGenres = (
        supabase.table("movie_genres")
        .select("genre")
        .eq("movie_id", movie_id)
        .execute()
        .data
    )
    movie_genre = set(genre["genre"] for genre in getGenres)

    # 현재 영화의 별점 정보
    getRating = (
        supabase.table("Ratings_Table")
        .select("rating")
        .eq("movieId", movie_id)
        .execute()
        .data
    )
    movie_rate = round(random.random() * 5, 1)
    if getRating:
        movie_rate = round(
            sum(rate["rating"] for rate in getRating) / len(getRating), 1
        )

    # 출연 배우, 감독관 정보
    tm_db_id = (
        supabase.table("Links_Table")
        .select("tmdbId")
        .eq("movieId", movie_id)
        .execute()
        .data
    )[0]["tmdbId"]
    movie_cast, movie_crew = init_crew_cast(tm_db_id)

    # 영화 태그 정보
    getTag = (
        supabase.table("Tags_Table")
        .select("tag")
        .eq("movieId", movie_id)
        .execute()
        .data
    )
    movie_tag = [data["tag"] for data in getTag]

    res = {
        MOVIE_TITLE: movie_title,
        MOVIE_POSTER: movie_poster,
        MOVIE_GENRE: movie_genre,
        MOVIE_TAGS: movie_tag,
        MOVIE_SCOPE: movie_rate,
        MOVIE_OVERVIEW: movie_overview,
        MOVIE_STORY: movie_story,
        MOVIE_CAST: movie_cast,
        MOVIE_CREW: movie_crew,
    }

    global g_total_movie_data
    g_total_movie_data[movie_id] = res


def init_multi_thread():
    """g_total_movie_data를 초기화하는 함수. 멀티 스레드를 이용."""
    total_data = (
        supabase.table("Movies_Table")
        .select("movieId", count="exact")
        .order("movieId", desc=False)
        .execute()
        .count
    )

    print(total_data)
    thread_count = 16
    for i in range(0, total_data, 1000):
        print(i, "/", total_data)

        res = (
            supabase.table("Movies_Table")
            .select("movieId, title, poster_url, overview, story_line")
            .order("movieId", desc=False)
            .range(i, i + 1000)
            .execute()
            .data
        )

        for j in range(0, len(res), thread_count):

            threads = []
            for k in range(j, j + thread_count):
                if k >= len(res):
                    continue

                thread = threading.Thread(target=init_job, args=(res[k],))
                threads.append(thread)
                thread.start()

            for t in threads:
                t.join()


def init_user_data():
    """모든 사용자 데이터를 초기화 함."""
    total_data = (
        supabase.table("userinfo")
        .select("id", count="exact")
        .order("id", desc=False)
        .execute()
        .count
    )

    print(total_data)

    for i in range(0, total_data, 1000):

        res = (
            supabase.table("userinfo")
            .select("id")
            .order("id", desc=False)
            .range(i, i + 1000)
            .execute()
            .data
        )

        for data in res:
            userId = data["id"]
            userGenre = []
            userStack = []
            getUserData = (
                supabase.table("Users_Table")
                .select("UserStack, UserTags")
                .eq("UserId", userId)
                .execute()
                .data
            )

            for userData in getUserData:
                userGenre.append(userData["UserTags"])
                userStack.append(userData["UserStack"])

            data = {USER_TAGS: userGenre, USER_STACK: userStack}

            g_total_user_data[userId] = data


if __name__ == "__main__":
    s = time.time()
    # init_multi_thread()
    init_user_data()
    e = time.time()
    print(f"{e - s:.3f}")

    # with open('mycsvfile.csv', 'w') as f:
    #     w = csv.writer(f)
    #
    #     w.writerow(['idx'] + g_total_movie_data[1].keys())
    #     for i in g_total_movie_data:
    #         w.writerow([i] + g_total_movie_data[i])
    # with open('res.txt', 'w') as file:
    #     for i in g_total_movie_data:
    #         file.write("movieId :" + str(i))
    #         file.write(json.dumps(g_total_movie_data[i]))

    print("len total data :", len(g_total_movie_data))
    # print(get_genre())
    print("=====toy story====")
    # print(g_total_movie_data[69849])
    pass


"""
더 이상 안 쓰이지만 혹시 몰라서 남겨 둔 함수들
"""


def _parse_poster(im_db_id, movieId):
    """
    imdb.com 에서 포스터 정보를 가져와서 Movies_Table 에 데이터 저장.
    (이미 초기화 해서 쓸일이 없음 혹시나 해서 남겨 둠)

    :param im_db_id: Links_Table imdbId 컬럼
    :param movieId: Links_Table movieId 컬럼
    :return: None
    """

    # 1차 파싱 : 메인 페이지에서 영화 포스터 링크 구하기
    URL = f"https://www.imdb.com/title/tt{im_db_id}/"
    response = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
    soup = bs(response.text, "html.parser")

    link = soup.find_all("a", class_="ipc-lockup-overlay")[0].get("href")

    # link 정보가 없으면 해당 영화가 imdb.com에 없음.
    if link:
        # 2차 파싱 : 영화 관련 목록에서 해당 사진을 가져옴.
        URL = "https://www.imdb.com" + link
        response = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
        soup = bs(response.text, "html.parser")

        poster_url = None
        for img in soup.find_all("img"):
            classes = set(img.get("class", []))
            if classes and "peek" not in classes:
                poster_url = img.get("src", None)
                break

        if poster_url:
            global supabase
            supabase.table("Movies_Table").update({"poster_url": poster_url}).eq(
                "movieId", movieId
            ).execute()
        else:
            print("find fail", movieId)
    else:
        print("link fail", movieId)


def _from_api(tm_db_id, movieId):
    """
    tmdb API를 통해서 영화 데이터(영화 포스터, 영화 상제 설명)를 가져와서 DB에 저장.
    (이미 초기화 해서 쓸일이 없음 혹시나 해서 남겨 둠)

    :param tm_db_id: Links_Table tmdbId 컬럼
    :param movieId: Links_Table movieId 컬럼
    :return: None
    """

    # DB에 tm_db가 없는 영화가 있음.
    if not tm_db_id:
        print("none_id :", movieId)
    else:
        response = requests.get(
            f"{POST_BASE_URL}/{tm_db_id}", params={"api_key": POST_API_KEY}
        ).json()

        new_data = {}
        if response.get("poster_path", None) is not None:
            new_data["poster_url"] = IMAGE_BASE_URL + response["poster_path"]

        if response.get("overview", None) is not None:
            new_data["overview"] = response["overview"]

        global supabase
        supabase.table("Movies_Table").update(new_data).eq("movieId", movieId).execute()


def _parse_overview_and_story_line(im_db_id, movieId, overview):
    """
    imdb.com 에서 파싱하여 overview랑 story_line 를 가져와서 DB에 저장.
    (이미 초기화 해서 쓸일이 없음 혹시나 해서 남겨 둠)

    :param im_db_id: Links_Table imdbId 컬럼
    :param movieId: Movies_Table movieId 컬럼
    :param overview: Movies_Table overview 컬럼
    :return: None
    """

    URL = f"https://www.imdb.com/title/tt{im_db_id}/plotsummary/"
    response = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
    soup = bs(response.text, "html.parser")

    elements = soup.select(
        "div.ipc-html-content-inner-div div.ipc-html-content-inner-div"
    )

    if len(elements) == 0:
        print(False, movieId)
    else:
        tmp_view = elements[0]
        tmp_story = elements[0] if len(elements) == 1 else elements[1]

        # story line 이 한개 인 경우
        if len(elements) >= 1:
            res = elements[0].find("span")
            if res:
                res.decompose()

            tmp_story = elements[0].get_text(separator=" ")
            tmp_view = tmp_story

        # story line 이 여러개 인 경우
        if len(elements) > 1:
            res = elements[1].find("span")
            if res:
                res.decompose()

            tmp_story = elements[1].get_text(separator=" ")

        # 기존 tmdb API 에서 overview 를 이미 설정한 경우, 원래대로 냅두기.
        tmp_view = overview if overview is not None else tmp_view

        new_data = {"overview": tmp_view, "story_line": tmp_story}

        global supabase
        supabase.table("Movies_Table").update(new_data).eq("movieId", movieId).execute()
