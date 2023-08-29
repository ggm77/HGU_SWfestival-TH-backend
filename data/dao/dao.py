async def getUserInfo(username):

    #get all of userinfo from db
    #db.get(username)

    #if nothing in there?

    user = {
        "username" : "testuser",
        "hashed_password" : "rqadfssd",
        "userType" : "user",
        "signUpDate" : "20230830",
        "email" : "testuser@raspinas.org.iptime",
        "locationX" : [0.0, 0.0],
        "postingList" : [1,2,3],
        "point" : 100,
        "disabled" : 0
    }

    return user