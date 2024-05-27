from role_db import g_get_rating

def get_rating():
    return g_get_rating()
    # return [{'movieId' : 'movieId_1' ,'rating' : 'rating_1'}, 
    #         {'movieId' : 'movieId_2' ,'rating' : 'rating_2'},
    #         {'movieId' : 'movieId_3' ,'rating' : 'rating_3'}]

#모든 영화ID와 평점 가져오기