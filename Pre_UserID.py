from role_db import g_get_user_id

def get_userid(uuid):
	return [g_get_user_id(uuid)]
	# return [{"UserId" : "UserId_1" ,"UserTags" : ["tag_1","tag_2","tag_3"]}]

#UserId : 로그인 한 유저의 UserId데이터, UserTags : 태그값은 여러개있을 수 있음.