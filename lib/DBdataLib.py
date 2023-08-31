from fastapi.encoders import jsonable_encoder

from DB.database import engineconn
from DB.models import *
from DB.models import userInfo


engine = engineconn()
session = engine.sessionmaker()



async def getUserInfo(userNumber):
    #if nothing in there?

    user = jsonable_encoder(session.query(userInfo).get(userNumber))
    return user

async def createUserInfo(user: dict):

    #create user
    

    #if created
    user = {
            "username" : "testuser",
            "userNumber" : 1, 
            "hashed_password" : "",
            "userType" : "user",
            "signUpDate" : "20230830",
            "email" : "testuser@raspinas.org.iptime",
            "location" : [0.0, 0.0],
            "point" : 100,
            "disabled" : 0
        }


    return await getUserInfo(user["userNumber"])


async def emailToUserNumber(email):
    return 1