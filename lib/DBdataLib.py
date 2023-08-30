
async def getUserInfo(email):

    #get all of userinfo from db
    #db.get(username)

    #if nothing in there?

    user = {
        "username" : "testuser",
        "userNumber" : 1, 
        "hashed_password" : "$2b$12$9fayMKgDg7H0k.GkdBP/ieUxVxBNJqWttxVVZ7fHTw8yyP/fla0bK",
        "userType" : "user",
        "signUpDate" : "20230830",
        "email" : "testuser@raspinas.org.iptime",
        "location" : [0.0, 0.0],
        "postingList" : [1,2,3],
        "chatList" : [1,2,3],
        "point" : 100,
        "disabled" : 0
    }

    return user
